import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Dict, Union, Optional

from astroid import List as ListNG
from astroid import (
    extract_node,
    Tuple,
    Const,
    For,
    While,
    Await,
    Call,
    Return,
    If,
    Match,
    MatchCase,
    Decorators,
    FunctionDef,
    AsyncFunctionDef,
    ClassDef,
)
from astroid.nodes.as_string import AsStringVisitor

from shelley.ast.devices import Device
from shelley.ast.rules import TriggerRuleFired
from shelley.shelleypy.checker.exceptions import ShelleyPyError
from shelley.shelleypy.visitors.visitor_helper import ShelleyCall
from shelley.shelleypy.visitors.visitor_helper import ShelleyOpDecorator
from shelley.shelleypy.visitors.visitor_helper import VisitorHelper
from shelley.shelleypy.visitors.visitor_helper import ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


@dataclass
class MethodDecoratorsVisitor(AsStringVisitor):
    method_name: str
    decorator: ShelleyOpDecorator = None

    def visit_decorators(self, node: Decorators) -> Any:
        for node in node.nodes:
            node.accept(self)

    def visit_call(self, node: Call) -> Any:
        # logger.debug(f"Method decorator: {node.func.name}")
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
class ClassDecoratorsVisitor(AsStringVisitor):
    external_only: bool
    uses: Dict[str, str] = field(default_factory=dict)
    system_claims: List[str] = field(default_factory=list)
    integration_claims: List[str] = field(default_factory=list)
    subsystem_claims: List[str] = field(default_factory=list)

    def visit_decorators(self, node: Decorators) -> Any:
        for node in node.nodes:
            node.accept(self)

    def visit_call(self, node: Call) -> Any:
        logger.debug(f"Decorator Call: {node.func.name}")
        decorator_name = node.func.name
        match decorator_name:
            case "claim":
                claim: str = node.args[0].value
                logger.debug(f"Claim: {claim}")
                claim = claim.removesuffix(";")
                if "system check" in claim and self.external_only:
                    self.system_claims.append(claim.removeprefix("system check"))
                elif "integration check" in claim and not self.external_only:
                    self.integration_claims.append(
                        claim.removeprefix("integration check")
                    )
                elif claim.startswith("subsystem") and not self.external_only:
                    parts = claim.split(" ")  # separate by spaces
                    name = parts[1]  # get subystem name from formula
                    parts = parts[3:]  # remove 'subsystem XX check' from string
                    claim = " ".join(parts)  # re-join by spaces
                    self.subsystem_claims.append((name, claim))
            case "system":
                for kw in node.keywords:
                    match kw.arg:
                        case "uses":
                            if not self.external_only:
                                for name, type in kw.value.items:
                                    self.uses[name.value] = type.value
                                    # TODO: melhorar isto?


@dataclass
class Python2ShelleyVisitor(AsStringVisitor):
    visitor_helper: VisitorHelper = field(init=False)
    external_only: bool = False
    extra_options: Dict = field(default_factory=dict)

    def __post_init__(self):
        self.vh = VisitorHelper(external_only=self.external_only)

    def py2shy(self, py_src) -> Device:
        if isinstance(py_src, Path):
            with py_src.open() as f:
                py_src = f.read()
        tree = extract_node(py_src)
        tree.accept(self)
        return self.vh.device

    def visit_classdef(self, node: ClassDef) -> Any:

        logger.debug(f"System name: {self.vh.device.name}")

        decorators_visitor = ClassDecoratorsVisitor(self.vh.external_only)
        node.decorators.accept(decorators_visitor)

        self.vh.context_system_init(
            node.name,
            decorators_visitor.uses,
            decorators_visitor.system_claims,
            decorators_visitor.integration_claims,
            decorators_visitor.subsystem_claims,
        )

        for node_body in node.body:  # process methods
            node_body.accept(self)

    def visit_asyncfunctiondef(self, node: AsyncFunctionDef) -> Any:
        self._handle_functiondef(node)

    def visit_functiondef(self, node: FunctionDef) -> Any:
        self._handle_functiondef(node)

    def _handle_functiondef(self, node: Union[FunctionDef, AsyncFunctionDef]):
        logger.debug(f"\n\n### Entering method: {node.name}")
        # logger.debug(node)

        # TODO: improve this
        if node.name in self.vh.device.events.list_str():
            raise ShelleyPyError(node.lineno, ShelleyPyError.DUPLICATED_METHOD)

        if node.decorators is None:
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        decorators_visitor = MethodDecoratorsVisitor(node.name)
        node.decorators.accept(decorators_visitor)

        if not decorators_visitor.decorator:
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        decorator = decorators_visitor.decorator

        if self.vh.is_base_system():  # base system, do not inspect body
            self.vh.register_new_operation(
                op_name=decorator.op_name,
                is_initial=decorator.is_initial,
                is_final=decorator.is_final,
                next_ops=decorator.next_ops,
            )
        else:  # system that contains subsystems, do inspect body
            assert type(node) in [
                FunctionDef,
                AsyncFunctionDef,
            ]  # this is just a safe check

            self.vh.context_init(node)
            # TODO: move this inside operation context
            self.vh.context_operation_init(decorator)

            for node_body in node.body:
                node_body.accept(self)

            # TODO: move this inside operation context
            self.vh.register_return_paths()
            self.vh.context_operation_end(node.lineno)
            self.vh.context_end()

        logger.debug(f"Leaving method: {node.name}")

    def visit_match(self, node: Match):
        logger.debug("Entering match")
        # logger.debug(node)

        #        my_context = self.vh.context_init(node)

        subject = node.subject
        if isinstance(subject, Await):
            subject = subject.value

        if not isinstance(subject, Call):  # check type of match call
            raise ShelleyPyError(subject.lineno, ShelleyPyError.MATCH_CALL_TYPE)

        # match call
        subject.accept(self)

        self.vh.set_match_call_to_last_call()

        all_branch_return = True
        for node_case in node.cases:
            case_ctx = self.vh.context_init(node, type=ContextTypes.BRANCH)
            node_case.accept(self)
            all_branch_return &= case_ctx.has_return
            self.vh.context_end()

        my_ctx = self.vh.current_context()  # TODO: new context for this?!
        my_ctx.current_path_merge(force_branch=self._extra_options_force_branch())
        my_ctx.has_return |= all_branch_return

        logger.debug("Leaving match")

    def _extra_options_force_branch(self):
        """
        If relax_match_force_case=True, then if there is a match with a single case, the case itself will be optional (xor branch).
        By default, force_branch is True (i.e., relax_match_force_case=False) for match statements, since we want to enforce at least one branch.
        """
        try:
            return not self.extra_options["relax_match_force_case"]
        except:
            return False

    def visit_matchcase(self, match_case_node: MatchCase):
        logger.debug("Entering matchcase")
        # logger.debug(match_case_node)

        my_ctx = self.vh.current_context()

        # before each case
        saved_match_call = self.vh.copy_match_call()

        # inspect case body
        first_node = True
        for matchcase_body_node in match_case_node.body:
            matchcase_body_node.accept(self)
            if first_node:
                first_node = False
                self.vh.check_case_first_node(
                    self._get_case_name(match_case_node), matchcase_body_node.lineno
                )

        # after each case
        self.vh.restore_match_call(saved_match_call)

        logger.debug("Leaving matchcase")

    def visit_await(self, node: Await):
        logger.debug(node)
        node.value.accept(self)

    def visit_call(self, node: Call):
        # logger.debug("Entering call")
        # logger.debug(node)
        # logger.debug(node.func)

        # TODO: improve this code?
        try:
            self.vh.last_call = ShelleyCall(
                exprself=node.func.expr.expr.name,
                subsystem_call=node.func.attrname,
                subsystem_instance=node.func.expr.attrname,
            )
        except AttributeError:
            logger.debug(f"    Ignoring Call: {node.func.repr_tree()}")
            return

        self.vh.register_new_call()
        # logger.debug(f"Found call: {str(self.vh.last_call)}")

    def visit_if(self, node: If):
        """ """
        # logger.debug(node)
        my_ctx = self.vh.current_context()
        all_branch_return = True

        logger.debug("Entering if")
        node.test.accept(self)  # test expression can be a subsys call
        if_ctx = self.vh.context_init(node, type=ContextTypes.BRANCH)
        for if_body_node in node.body:
            if_body_node.accept(self)
        all_branch_return &= if_ctx.has_return
        self.vh.context_end()
        logger.debug("Leaving if")

        if len(node.orelse) != 0:
            logger.debug("Entering else")
            else_ctx = self.vh.context_init(node, type=ContextTypes.BRANCH)
            for else_body_node in node.orelse:
                else_body_node.accept(self)
            all_branch_return &= else_ctx.has_return
            self.vh.context_end()
            logger.debug("Leaving else")
        else:
            my_ctx.branch_path.add_choice(TriggerRuleFired())


        my_ctx.current_path_merge()  # TODO: new context for this?!

        my_ctx.has_return |= all_branch_return

        logger.debug("Leaving if/else")

    def visit_for(self, node: For):
        logger.debug("entering for")
        self._handle_loop(node)
        logger.debug("leaving for")

    def visit_while(self, node: While):
        logger.debug("entering while")
        self._handle_loop(node)
        logger.debug("leaving while")

    def _handle_loop(self, node: Union[For, While]):
        # logger.debug(node)
        my_ctx = self.vh.current_context()
        all_branch_return = True

        for_body_ctx = self.vh.context_init(node, type=ContextTypes.LOOP)
        for node_for_body in node.body:
            node_for_body.accept(self)
        all_branch_return &= for_body_ctx.has_return
        self.vh.context_end()

        if node.orelse:
            for_else_ctx = self.vh.context_init(node, type=ContextTypes.LOOP_ELSE)
            for node_for_else in node.orelse:
                node_for_else.accept(self)
            all_branch_return &= for_else_ctx.has_return
            self.vh.context_end()

        if all_branch_return:
            raise ShelleyPyError(node.lineno, ShelleyPyError.ALL_BRANCH_RETURN_INSIDE_LOOP)

        my_ctx.has_return |= all_branch_return

        self.vh.current_context().current_path_merge()  # TODO: new context for this?!

    def visit_return(self, node: Return):
        """
        For now, let's create a Shelley operation for each return.
        An alternative (smarter but more difficult to implement) approach would be to create a Shelley operation
        for each "type" of return.
        """
        # logger.debug(node)
        return_next: List[str] = self._parse_return_value(node)
        self.vh.current_context().return_path_put(return_next, node.lineno)

    @staticmethod
    def _get_case_name(match_case_node: MatchCase):
        """
        MatchCase -> pattern -> MatchValue -> value -> Const -> value => str
        """
        try:
            case_name: str = match_case_node.pattern.value.value
            if not isinstance(case_name, str):  # check type of match case value
                raise ShelleyPyError(
                    match_case_node.pattern.lineno, ShelleyPyError.MATCH_CASE_VALUE_TYPE
                )
        except AttributeError:
            raise ShelleyPyError(
                match_case_node.pattern.lineno, ShelleyPyError.MATCH_CASE_VALUE_TYPE
            )
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
