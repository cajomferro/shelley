import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

from astroid import List as ListNG
from astroid import (
    Tuple,
    Const,
    For,
    Await,
    Call,
    Return,
    Expr,
    If,
    Match,
    MatchCase,
    Decorators,
    FunctionDef,
    ClassDef,
    NodeNG,
    extract_node
)
from shelley.shelleypy.visitors import ShelleyCall
from shelley.shelleypy.visitors import ShelleyOpDecorator
from shelley.shelleypy.visitors import ShelleyPyError
from shelley.shelleypy.visitors import VisitorHelper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


@dataclass
class MethodDecoratorsVisitor(NodeNG):
    method_name: str
    decorator: ShelleyOpDecorator = None

    def visit_decorators(self, node: Decorators) -> Any:
        for node in node.nodes:
            node.accept(self)

    def visit_call(self, node: Call) -> Any:
        logger.debug(f"Method decorator: {node.func.name}")
        if node.func.name == "operation":
            self.decorator = ShelleyOpDecorator(self.method_name)
            for kw in node.keywords:
                match kw.arg:
                    case "initial":
                        self.decorator.is_initial = True
                    case "final":
                        self.decorator.is_final = True
                    case "next":
                        self.decorator.next_ops = [op.value for op in kw.value.elts]


@dataclass
class ClassDecoratorsVisitor(NodeNG):
    external_only: bool

    def visit_decorators(self, node: Decorators) -> Any:
        for node in node.nodes:
            node.accept(self)

    def visit_call(self, node: Call) -> Any:
        logger.debug(f"Decorator Call: {node.func.name}")
        decorator_name = node.func.name
        self.uses = dict()
        self.system_claims = []
        self.integration_claims = []
        self.subsystem_claims = []
        match decorator_name:
            case "claim":
                claim: str = node.args[0].value
                logger.debug(f"Claim: {claim}")
                claim = claim.removesuffix(";")
                if "system check" in claim and self.external_only:
                    self.system_claims.append(claim.removeprefix("system check"))
                elif "integration check" in claim and not self.external_only:
                    self.integration_claims.append(claim.removeprefix("integration check"))
                elif claim.startswith("subsystem") and not self.external_only:
                    parts = claim.split(" ")  # separate by spaces
                    name = parts[1]  # get subystem name from formula
                    parts = parts[3:]  # remove 'subsystem XX check' from string
                    claim = " ".join(parts)  # re-join by spaces
                    self.subsystem_claims.append(claim)
            case "system":
                for kw in node.keywords:
                    match kw.arg:
                        case "uses":
                            if not self.external_only:
                                for name, type in kw.value.items:
                                    self.uses[name.value] = type.value
                                    # TODO: melhorar isto?


@dataclass
class Python2ShelleyVisitor(NodeNG):
    visitor_helper: VisitorHelper

    def visit_classdef(self, node: ClassDef) -> Any:

        logger.debug(f"System name: {self.visitor_helper.device.name}")

        decorators_visitor = ClassDecoratorsVisitor(self.visitor_helper.external_only)
        node.decorators.accept(decorators_visitor)

        self.visitor_helper.context_system_init(node.name, decorators_visitor.uses,
                                                decorators_visitor.system_claims,
                                                decorators_visitor.integration_claims,
                                                decorators_visitor.subsystem_claims)

        for node in node.body:  # process methods
            node.accept(self)

    def visit_functiondef(self, node: FunctionDef) -> Any:
        logger.debug(f"Method: {node.name}")
        logger.debug(node)

        if node.decorators is None:
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        decorators_visitor = MethodDecoratorsVisitor(node.name)
        node.decorators.accept(decorators_visitor)

        if not decorators_visitor.decorator:
            raise ShelleyPyError(node.decorators.lineno, ShelleyPyError.DECORATOR_PARSE_ERROR)

        decorator = decorators_visitor.decorator
        self.visitor_helper.context_operation_init(decorator)

        if self.visitor_helper.is_base_system():  # base system, do not inspect body
            self.visitor_helper.register_new_operation(op_name=decorator.op_name, is_initial=decorator.is_initial,
                                                       is_final=decorator.is_final, next_ops=decorator.next_ops)
        else:  # system that contains subsystems, do inspect body
            assert type(node) == FunctionDef  # this is just a safe check
            for node in node.body:
                node.accept(self)

            if not self.visitor_helper.context_operation_end():
                raise ShelleyPyError(node.lineno, ShelleyPyError.MISSING_RETURN)

    def visit_match(self, node: Match):
        logger.debug(node)
        self.visitor_helper.context_match_init()

        node.subject.accept(self)
        if not isinstance(self.visitor_helper.last_call.node_call, Call):  # check type of match call
            raise ShelleyPyError(node.subject.lineno, ShelleyPyError.MATCH_CALL_TYPE)

        self.visitor_helper.current_match_call = self.visitor_helper.last_call

        for node_case in node.cases:
            node_case.accept(self)

        self.visitor_helper.context_match_end()

    def visit_matchcase(self, match_case_node: MatchCase):
        logger.debug(match_case_node)

        self.visitor_helper.context_match_case_init()

        # inspect case body
        first_node = True
        for matchcase_body_node in match_case_node.body:
            matchcase_body_node.accept(self)
            if first_node:
                first_node = False
                self.visitor_helper.check_case_first_node(self._get_case_name(match_case_node), matchcase_body_node.lineno)

        self.visitor_helper.context_match_case_end()

        if not self.visitor_helper.n_returns:
            raise ShelleyPyError(match_case_node.lineno, ShelleyPyError.CASE_MISSING_RETURN)

    def visit_await(self, node: Await):
        logger.debug(node)
        node.value.accept(self)

    def visit_call(self, node: Call):
        logger.debug(node)

        # TODO: improve this code?
        try:
            self.visitor_helper.last_call = ShelleyCall(node)
        except AttributeError:
            logger.debug(f"    Ignoring Call: {node.func.repr_tree()}")
            return

        self.visitor_helper.register_new_call()

    def visit_if(self, node: If):
        """
        # TODO: elif is currently not supported!
        """
        logger.debug(node)
        for if_body_node in node.body:
            if_body_node.accept(self)

        logger.debug(node)
        for else_body_node in node.orelse:
            else_body_node.accept(self)

        logger.debug(node)

    def visit_for(self, node: For):
        logger.debug(node)
        self.visitor_helper.context_for_init()
        for node_for_body in node.body:
            node_for_body.accept(self)

        if self.visitor_helper.n_returns:
            raise ShelleyPyError(
                node.lineno, "Return statements are not allowed inside loops!"
            )

        self.visitor_helper.register_new_for()

    def visit_expr(self, node: Expr):
        logger.debug(node)
        node.value.accept(self)

    def visit_return(self, node: Return):
        """
        For now, let's create a Shelley operation for each return.
        An alternative (smarter but more difficult to implement) approach would be to create a Shelley operation
        for each "type" of return.
        """
        logger.debug(node)
        return_next: List[str] = self._parse_return_value(node)
        logger.debug(f"Parsed return: {return_next}")
        if not self.visitor_helper.register_new_return(return_next):
            raise ShelleyPyError(
                node.lineno,
                f"Return names {return_next} do not match possible next operations {self.visitor_helper.current_op_decorator.next_ops}!",
            )

    @staticmethod
    def _get_case_name(match_case_node: MatchCase):
        """
        MatchCase -> pattern -> MatchValue -> value -> Const -> value => str
        """
        try:
            case_name: str = match_case_node.pattern.value.value
            if not isinstance(case_name, str):  # check type of match case value
                raise ShelleyPyError(match_case_node.pattern.lineno, ShelleyPyError.MATCH_CASE_VALUE_TYPE)
        except AttributeError:
            raise ShelleyPyError(match_case_node.pattern.lineno, ShelleyPyError.MATCH_CASE_VALUE_TYPE)
        return case_name

    @staticmethod
    def _parse_return_value(node: Return):
        node_value = node.value
        if isinstance(node.value, Tuple):
            next_op_node = node.value.elts[0]
        else:
            next_op_node = node_value

        if isinstance(next_op_node, Const) and isinstance(next_op_node.value, str):
            value: List[str] = [next_op_node.value]
        elif isinstance(next_op_node, ListNG):
            value: List[str] = [x.value for x in next_op_node.elts]
        else:
            raise ShelleyPyError(node_value.lineno, ShelleyPyError.RETURN_PARSE_ERROR)

        return value


def main():
    logger.setLevel(logging.INFO)

    # src_path = Path("/app/shelley-examples/micropython_paper_full_example/valve.py")
    src_path = Path("/app/shelley-examples/micropython_paper_full_example/vhandler_full.py")

    with src_path.open() as f:
        tree = extract_node(f.read())

    visitor_helper = VisitorHelper(external_only=False)
    p2s_visitor = Python2ShelleyVisitor(visitor_helper)

    try:
        tree.accept(p2s_visitor)
    except ShelleyPyError as error:
        logger.error(f"{error.msg} (l. {error.lineno})")
        sys.exit(os.EX_SOFTWARE)

    device = visitor_helper.device

    from shelley.ast.visitors.pprint import PrettyPrintVisitor
    visitor = PrettyPrintVisitor(components=device.components)
    device.accept(visitor)
    logger.info(visitor.result.strip())


if __name__ == '__main__':
    main()
