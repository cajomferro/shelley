import sys, os
from typing import List, Optional, Dict, Union, Any
from pathlib import Path
import logging

import astroid
import yaml
import copy

from astroid import (
    parse,
    extract_node,
    AsyncFunctionDef,
    FunctionDef,
    Expr,
    Match,
    Await,
    Call,
    If,
    Return,
    ClassDef,
    Decorators,
    AnnAssign,
    MatchSequence,
    MatchCase,
    MatchValue,
    Const,
)

from lark import Lark

from shelley.shelleypy.checker.exceptions import CompilationError

from shelley.parsers.ltlf_lark_parser import LTLParser
from shelley.parsers import ltlf_lark_parser

from shelley.ast.devices import Device
from shelley.ast.events import Events, Event
from shelley.ast.devices import discover_uses
from shelley.ast.behaviors import Behaviors
from shelley.ast.triggers import Triggers, TriggerRule
from shelley.ast.rules import (
    TriggerRuleSequence,
    TriggerRuleEvent,
    TriggerRuleFired,
    TriggerRuleChoice,
)
from shelley.ast.components import Components, Component
from shelley.ast.visitors.shelley2lark import Shelley2Lark

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyshelley")


def exit_with_error(lineno: int, msg: str):
    logger.error(f"{msg} (l. {lineno})")
    sys.exit(os.EX_SOFTWARE)

def warning(lineno: int, msg: str):
    logger.warning(f"{msg} (l. {lineno})")

def parse_uses(uses_path: Optional[Path]) -> Dict[str, str]:
    if uses_path is None:
        return {}

    uses: Dict[str, str]
    with uses_path.open(mode="r") as f:
        uses = yaml.safe_load(f)

    if uses is None:
        return {}  # empty or commented yaml
    elif isinstance(uses, dict):
        return uses
    else:
        raise CompilationError(
            "Shelley parser error: uses file must be a valid dictionary"
        )


class PyVisitor:
    def __init__(self, external_only=False):
        self.external_only = external_only
        self.device = Device(
            name="",
            events=Events(),
            behaviors=Behaviors(),
            triggers=Triggers(),
            components=Components(),
        )
        self._current_operation: Optional[str] = None
        self._current_rule: TriggerRule = TriggerRuleFired()
        self.ltlf_parser = Lark.open(
            "ltlf_grammar.lark", rel_to=ltlf_lark_parser.__file__, start="formula"
        ).parse
        self._current_method_node: Optional[
            Union[astroid.FunctionDef, astroid.AsyncFunctionDef]
        ] = None
        self._current_op_decorator: Optional[Dict[str, Any]] = None
        self._method_return_idx: int = 0
        self.n_returns: int = 0
        self._collect_extra_ops: Dict[str, Any] = dict()
        self._saved_operations = list()

    def _create_operation(self, name, is_initial, is_final, next_ops_list, rules):
        current_operation: Event = self.device.events.create(
            name,
            is_start=is_initial,
            is_final=is_final,
        )

        if len(next_ops_list) == 0:
            self.device.behaviors.create(
                copy.copy(current_operation)
            )  # operation without next operations

        for next_op in next_ops_list:
            self.device.behaviors.create(
                copy.copy(current_operation),
                Event(
                    name=next_op,
                    is_start=False,
                    is_final=True,
                ),
            )

        self.device.triggers.create(copy.copy(current_operation), copy.copy(rules))

    def _create_operations(
        self, node: Union[astroid.FunctionDef, astroid.AsyncFunctionDef]
    ):
        # for single-return methods, use the name of the method
        if len(self._collect_extra_ops) == 1:
            self._create_operation(
                node.name,
                self._current_op_decorator["initial"],
                self._current_op_decorator["final"],
                self._current_op_decorator["next"],
                self._collect_extra_ops[self._current_operation]["rules"],
            )
        else:  # for multiple-return methods, use the name of the extra operations...
            for extra_op_name, extra_op_info in self._collect_extra_ops.items():
                self._create_operation(
                    extra_op_name,
                    False,
                    self._current_op_decorator["final"],
                    extra_op_info["next"],
                    extra_op_info["rules"],
                )
            # ... and map the original operation with the extra operations
            self._create_operation(
                node.name,
                self._current_op_decorator["initial"],
                False,
                [extra_op_name for extra_op_name in self._collect_extra_ops.keys()],
                TriggerRuleFired(),
            )

        self._collect_extra_ops = dict()

    def _process_operation(
        self, node: Union[astroid.FunctionDef, astroid.AsyncFunctionDef]
    ):
        def show_error():
            logger.debug(f"Skipping. This method is not annotated as an operation!")

        logger.debug(f"Method: {node.name}")

        if not node.decorators:
            show_error()
            return

        self._current_op_decorator = self.find(node.decorators)
        if not self._current_op_decorator:
            show_error()
            return

        if not self._current_op_decorator["type"] == "operation":
            show_error()
            return

        self._current_op_decorator["name"] = node.name
        self._method_return_idx = 0

        if (
            len(self.device.uses) == 0
        ) or self.external_only:  # base system, do not inspect body
            self._create_operation(
                node.name,
                self._current_op_decorator["initial"],
                self._current_op_decorator["final"],
                self._current_op_decorator["next"],
                TriggerRuleFired(),
            )
        else:
            for x in node.body:
                self.find(x)  # inspect body

            self._create_operations(node)

            if self.n_returns == 0:
                exit_with_error(node.lineno, "Missing return!")

        self._current_rule = TriggerRuleFired()
        self._saved_operations = list()

    def _process_decorators(self, node):
        for x in node.nodes:
            if isinstance(x, Call):
                match x.func.name:
                    case "claim":
                        claim: str = x.args[0].value
                        logger.debug(f"Claim: {claim}")
                        claim = claim.removesuffix(";")
                        if "system check" in claim and self.external_only:
                            claim = claim.removeprefix("system check")
                            formula = LTLParser().transform(self.ltlf_parser(claim))
                            self.device.system_formulae.append(formula)
                        elif "integration check" in claim and not self.external_only:
                            claim = claim.removeprefix("integration check")
                            formula = LTLParser().transform(self.ltlf_parser(claim))
                            self.device.integration_formulae.append(formula)
                        elif claim.startswith("subsystem") and not self.external_only:
                            parts = claim.split(" ")  # separate by spaces
                            name = parts[1]  # get subystem name from formula
                            parts = parts[
                                3:
                            ]  # remove 'subsystem XX check' from string
                            claim = " ".join(parts)  # re-join by spaces
                            formula = LTLParser().transform(self.ltlf_parser(claim))
                            self.device.subsystem_formulae.append((name, formula))

                    case "operation":
                        decorator = {
                            "type": "operation",
                            "initial": False,
                            "final": False,
                            "next": [],
                        }
                        for kw in x.keywords:
                            match kw.arg:
                                case "initial":
                                    decorator["initial"] = True
                                case "final":
                                    decorator["final"] = True
                                case "next":
                                    decorator["next"] = [
                                        op.value for op in kw.value.elts
                                    ]
                        return decorator
                    case "system":
                        for kw in x.keywords:
                            match kw.arg:
                                case "uses":
                                    if not self.external_only:
                                        for name, type in kw.value.items:
                                            self.device.components.create(
                                                name.value, type.value
                                            )
                                            self.device.uses = discover_uses(
                                                self.device.components
                                            )  # TODO: melhorar isto?

    def _process_return(self, node):
        """
        For now, let's create a Shelley operation for each return.
        An alternative (smarter but more difficult to implement) approach would be to create a Shelley operation
        for each "type" of return.
        """
        if isinstance(node.value, Const):
            return_next: List[str] = [(node.value.value)]
        else:
            return_next: List[str] = [x.value for x in node.value.elts]

        self._method_return_idx += 1
        operation_name: str = (
            f"{self._current_op_decorator['name']}_{self._method_return_idx}"
        )

        logger.debug(f" Operation: {operation_name}")

        self._current_operation = operation_name
        self._saved_operations.append(self._current_operation)
        self._collect_extra_ops[operation_name] = {
            "next": return_next,
            "rules": self._current_rule,
        }

        next_ops_list = self._current_op_decorator["next"]
        if next_ops_list and not all(elem in next_ops_list for elem in return_next):
            exit_with_error(node.lineno, f"Return names {return_next} do not match possible next operations {next_ops_list}!")

        self.n_returns += 1

    def _process_if(self, node: astroid.NodeNG):
        # TODO: add support for choice with more than 2 branches
        # TODO: handle when one of the branches has return and the other not OR do not allow this
        save_rule: TriggerRule = copy.copy(self._current_rule)

        self._current_rule = TriggerRuleFired()
        logger.debug("If")
        for x in node.body:
            self.find(x)
        left_rule = copy.copy(self._current_rule)

        self._current_rule = TriggerRuleFired()
        logger.debug("Else")
        for x in node.orelse:
            self.find(x)
        right_rule = copy.copy(self._current_rule)

        self._current_rule = save_rule

        if isinstance(left_rule, TriggerRuleFired):
            next_rule = right_rule
        elif isinstance(right_rule, TriggerRuleFired):
            next_rule = left_rule
        else:
            next_rule = TriggerRuleChoice()
            next_rule.choices.extend([left_rule, right_rule])

        match self._current_rule:
            case TriggerRuleFired():
                self._current_rule = next_rule
            case TriggerRule():  # any other type of rule
                self._current_rule = TriggerRuleSequence(self._current_rule, next_rule)

        match self.n_returns:
            case 2: # assuming both if/else have return statements
                for op_name in self._saved_operations:
                    try:
                        old_rule = self._collect_extra_ops[op_name]["rules"]
                        new_rule = TriggerRuleSequence(save_rule, old_rule)
                        self._collect_extra_ops[op_name].update({"rules": new_rule})
                    except KeyError:
                        pass
                self._saved_operations = list()
            case 1:
                exit_with_error(node.lineno, "One of the if/else branches has return and the other not!")

    def _check_case(self, case: astroid.MatchCase, match_call: str):
        first_node = case.body[0]
        if isinstance(case.pattern, MatchValue):
            case_name = case.pattern.value.value  # this must be a string!

            match_exprself, match_subystem_instance, _ = match_call.split(".")

            # the first call name SHOULD match the case name
            # assert isinstance(first_node,
            #                   Expr), f"Expecting Expr in line {first_node.lineno}, found {type(first_node)}!"
            if isinstance(first_node.value, Await):
                first_node = first_node.value
            # assert isinstance(first_node.value,
            #                   Call), f"Expecting Expr.Call in line {first_node.lineno}, found {type(first_node.value)}!"

            if isinstance(first_node.value, Call):
                first_node = first_node.value.func
                first_node_subystem_call = first_node.attrname
                first_node_subystem_instance = first_node.expr.attrname
                first_node_exprself = first_node.expr.expr.name
                first_node_call_name = f"{first_node_exprself}.{first_node_subystem_instance}.{first_node_subystem_call}"
                expected_call_name = (
                    f"{match_exprself}.{match_subystem_instance}.{case_name}"
                )

                if not first_node_call_name == expected_call_name:
                    logger.warning(
                        f"PyShelley warning in line {first_node.lineno}: Expecting {expected_call_name} but found {first_node_call_name}. The first subsystem call should match the case name!"
                    )
            # try:
            #     assert first_node_call_name == expected_call_name
            # except AssertionError:
            #     sys.exit(
            #         f"PyShelley error in line {first_node.lineno}.\nExpecting {expected_call_name} but found {first_node_call_name}. The first subsystem call must match the case name!"
            #     )
        else:
            # try:
            #     assert len(case.body) == 1
            #     assert isinstance(first_node, Return)
            # except AssertionError:
            sys.exit(
                f"PyShelley error in line {first_node.lineno}: Cases with several options are not supported!"
            )

    def _process_match_cases(
        self, match_call: str, node_cases: List[astroid.MatchCase]
    ):
        save_rule: TriggerRule = copy.copy(self._current_rule)
        for case in node_cases:
            logger.debug(f"Match case: {case.pattern}")
            self._current_rule = save_rule
            self.n_returns = 0  # we must have a return for each match case

            self._check_case(case, match_call)

            for x in case.body:
                self.find(x)

            self._collect_extra_ops[self._current_operation].update(
                {"rules": self._current_rule}
            )
            self._current_rule = TriggerRuleFired()

            if not self.n_returns:
                sys.exit(
                    f"PyShelley error\nExpecting return after line {x.lineno}. Did you forget the return statement in this case?"
                )

    def _process_call(self, node: Call):
        try:
            subystem_call = node.func.attrname
            subystem_instance = node.func.expr.attrname
            exprself = node.func.expr.expr.name
            call_name = f"{exprself}.{subystem_instance}.{subystem_call}"
        except AttributeError:
            logger.debug(f"    Ignoring Call: {node.func.repr_tree()}")
            return

        try:
            component: Component = self.device.components[subystem_instance]
        except KeyError as err:
            logger.debug(f"    Ignoring Call: {call_name}")
            return

        match self._current_rule:
            case TriggerRuleFired():
                self._current_rule = TriggerRuleEvent(component, subystem_call)
            case TriggerRule():  # any other type of rule
                self._current_rule = TriggerRuleSequence(
                    self._current_rule,
                    TriggerRuleEvent(component, subystem_call),
                )

        logger.debug(f"Call: {call_name}")
        return f"{call_name}"

    def find(self, node, expects_node_type=None, **kwargs):
        if expects_node_type:
            assert (
                type(node) in expects_node_type
            ), f"Expecting node type {expects_node_type} but found {type(node)}"

        ret = None

        match node:
            # TODO: case func=__init__ check if subsystems are well declared

            case ClassDef():
                self.device.name = node.name
                logger.debug(f"System name: {self.device.name}")
                self.find(node.decorators)
                for x in node.body:
                    self.find(x)
            case AsyncFunctionDef():
                self._process_operation(node)
            case FunctionDef():
                self._process_operation(node)
            case Decorators():
                ret = self._process_decorators(node)
            case AnnAssign():
                self.find(node.value)
            case Expr():
                self.find(node.value)
            case Call():
                ret = self._process_call(node)
            case Await():
                logger.debug(f"Await")
                ret = self.find(node.value)
            case Match():
                logger.debug(f"Match")
                match_call = self.find(node.subject, expects_node_types=[Call, Await])
                self._process_match_cases(match_call, node.cases)
            case Return():
                self._process_return(node)
                logger.debug(f"Return")
            case If():
                self._process_if(node)
        return ret


# class PyVisitorInternal(PyVisitor):
#     def _process_match_cases(
#         self, match_call: str, node_cases: List[astroid.MatchCase]
#     ):
#         save_rule: TriggerRule = copy.copy(self._current_rule)
#         for case in node_cases:
#             logger.debug(f"    Match case: {case.pattern}")
#             self._current_rule = save_rule
#             self._return_check = False  # we must have a return for each match case
#
#             self._check_case(case, match_call)
#
#             for x in case.body:
#                 self.find(x)
#
#             if not self._return_check:
#                 sys.exit(
#                     f"PyShelley error\nExpecting return after line {x.lineno}. Did you forget the return statement in this case?"
#                 )
#
#     def _create_operations(
#         self, node: Union[astroid.FunctionDef, astroid.AsyncFunctionDef]
#     ):
#         # for single-return methods, use the name of the method
#         if len(self._collect_extra_ops) == 1:
#             self._create_operation(
#                 node.name,
#                 self._current_op_decorator["initial"],
#                 self._current_op_decorator["final"],
#                 self._current_op_decorator["next"],
#                 self._collect_extra_ops[0]["rules"],
#             )
#         else:  # for multiple-return methods, use the name of the extra operations...
#             for extra_op in self._collect_extra_ops:
#                 self._create_operation(
#                     extra_op["name"],
#                     False,
#                     self._current_op_decorator["final"],
#                     extra_op["next"],
#                     extra_op["rules"],
#                 )
#             # ... and map the original operation with the extra operations
#             self._create_operation(
#                 node.name,
#                 self._current_op_decorator["initial"],
#                 False,
#                 [extra_op["name"] for extra_op in self._collect_extra_ops],
#                 TriggerRuleFired(),
#             )
#
#         self._collect_extra_ops = []


# class PyVisitorExternal(PyVisitor):
#     def _process_match_cases(
#         self, match_call: str, node_cases: List[astroid.MatchCase]
#     ):
#         save_rule: TriggerRule = copy.copy(self._current_rule)
#         self._current_rule = TriggerRuleFired()
#         branches_rules: List[TriggerRule] = list()
#         for case in node_cases:
#             logger.debug(f"    Match case: {case.pattern}")
#             self._check_case(case, match_call)
#             for x in case.body:
#                 self.find(x)
#             if not isinstance(self._current_rule, TriggerRuleFired):
#                 branches_rules.append(copy.copy(self._current_rule))
#             self._current_rule = TriggerRuleFired()
#         self._current_rule = save_rule  # restore rule before finding match cases
#         if len(branches_rules) > 0:  # only proceed if match cases have calls inside
#             choice_rule = TriggerRuleChoice()
#             choice_rule.choices.extend(branches_rules)
#             # finally, append the choices rule to a previously rule or not
#             match self._current_rule:
#                 case TriggerRuleFired():
#                     self._current_rule = choice_rule
#                 case TriggerRule():  # any other type of rule previously existent
#                     self._current_rule = TriggerRuleSequence(
#                         self._current_rule, choice_rule
#                     )
#
#     def _create_operations(
#         self, node: Union[astroid.FunctionDef, astroid.AsyncFunctionDef]
#     ):
#         self._create_operation(
#             node.name,
#             self._current_op_decorator["initial"],
#             self._current_op_decorator["final"],
#             self._current_op_decorator["next"],
#             self._current_rule,
#         )
#         self.current_rule = TriggerRuleFired()
#
#
def process_visitor(tree, output_path: Path, external_only=False):
    svis = PyVisitor(external_only)
    svis.find(tree)

    # visitor = PrettyPrintVisitor(components=svis.device.components)
    # svis.device.accept(visitor)
    # logger.info(visitor.result.strip())

    visitor = Shelley2Lark(components=svis.device.components)
    svis.device.accept(visitor)

    lark_code = visitor.result.strip()
    # print(lark_code)

    with output_path.open("w") as f:
        f.write(lark_code)


def check(src_path: Path, uses_path: Path, output_path: Path):
    uses = parse_uses(uses_path)
    logger.debug(f"Uses: {uses}")

    with src_path.open() as f:
        tree = extract_node(f.read())

    # print(tree.repr_tree())
    process_visitor(tree, Path(output_path.parent, f"integration_{output_path.name}"))
    process_visitor(tree, output_path, external_only=True)

    # for x in svis.device.system_formulae:
    #     print(ltlf_lark_parser.dumps(x, nusvm_strict=False))
    #
    # for x in svis.device.integration_formulae:
    #     print(ltlf_lark_parser.dumps(x, nusvm_strict=False))
