import sys
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
)

from lark import Lark, Transformer

from shelley.shelleypy.checker.exceptions import CompilationError

from shelley.parsers.ltlf_lark_parser import LTLParser
from shelley.parsers import ltlf_lark_parser
from shelley.parsers import errors

from shelley.ast.devices import Device
from shelley.ast.events import Events, Event
from shelley.ast.actions import Actions, Action
from shelley.ast.devices import discover_uses
from shelley.ast.behaviors import Behaviors, Behavior
from shelley.ast.triggers import Triggers, Trigger, TriggerRule
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


class StrangeVisitor:
    def __init__(self):
        self.device = Device(
            name="",
            events=Events(),
            behaviors=Behaviors(),
            triggers=Triggers(),
            components=Components(),
        )
        self.current_operation: Optional[Event] = None
        self.current_rule: TriggerRule = TriggerRuleFired()
        self.ltlf_parser = Lark.open(
            "ltlf_grammar.lark", rel_to=ltlf_lark_parser.__file__, start="formula"
        ).parse
        self._current_method_node: Optional[
            Union[astroid.FunctionDef, astroid.AsyncFunctionDef]
        ] = None
        self._current_op_decorator: Optional[Dict[str, Any]] = None
        self._method_return_idx: int = 0
        self._return_check: bool = False
        self._collect_extra_ops: List[Dict[str, Any]] = list()

    def print_call(self, parent_name, func_call: Call):
        subystem_call = func_call.func.attrname
        subystem_instance = func_call.func.expr.attrname
        exprself = func_call.func.expr.expr.name
        logger.debug(
            f"    {parent_name} call: {exprself}.{subystem_instance}.{subystem_call}"
        )

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

    def _process_operation(
        self, node: Union[astroid.FunctionDef, astroid.AsyncFunctionDef]
    ):
        if node.decorators:
            self._current_op_decorator = self.find(node.decorators)
            assert self._current_op_decorator["type"] == "operation"
            self._current_op_decorator["name"] = node.name
            logger.debug(f"Method: {node.name}")
            self._method_return_idx = 0

            if len(self.device.uses) == 0:  # base system, do not inspect body
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

                # for single-return methods, use the name of the method
                if len(self._collect_extra_ops) == 1:
                    self._create_operation(
                        node.name,
                        self._current_op_decorator["initial"],
                        self._current_op_decorator["final"],
                        self._current_op_decorator["next"],
                        self._collect_extra_ops[0]["rules"],
                    )
                else:  # for multiple-return methods, use the name of the extra operations...
                    for extra_op in self._collect_extra_ops:
                        self._create_operation(
                            extra_op["name"],
                            False,
                            self._current_op_decorator["final"],
                            extra_op["next"],
                            extra_op["rules"],
                        )
                    # ... and map the original operation with the extra operations
                    self._create_operation(
                        node.name,
                        self._current_op_decorator["initial"],
                        False,
                        [extra_op["name"] for extra_op in self._collect_extra_ops],
                        TriggerRuleFired(),
                    )

                self._collect_extra_ops = []
        else:
            logger.debug(
                f"Found method {node.name} but it is not annotated as an operation!"
            )

    def _process_return(self, node):
        """
        For now, let's create a Shelley operation for each return.
        An alternative (smarter but more difficult to implement) approach would be to create a Shelley operation
        for each "type" of return.
        """
        return_next: str = (
            node.value.value
        )  # TODO: for now, we just accept single-string return
        self._method_return_idx += 1
        operation_name: str = f"{self._current_op_decorator['name']}_{return_next}_{self._method_return_idx}"

        logger.debug(f"    Operation: {operation_name}")

        self._collect_extra_ops.append(
            {"name": operation_name, "next": [return_next], "rules": self.current_rule}
        )

        next_ops_list = self._current_op_decorator["next"]
        if next_ops_list and not return_next in next_ops_list:
            sys.exit(
                f"PyShelley error\nReturn name '{return_next}' does not match possible next operations in line {node.lineno}!"
            )

        self.current_rule = TriggerRuleFired()
        self._return_check = True

    def _process_decorators(self, node):
        for x in node.nodes:
            if isinstance(x, Call):
                match x.func.name:
                    case "claim":
                        claim: str = x.args[0].value
                        logger.debug(f"Claim: {claim}")
                        claim = claim.removesuffix(";")
                        if "system check" in claim:
                            claim = claim.removeprefix("system check")
                            formula = LTLParser().transform(self.ltlf_parser(claim))
                            self.device.system_formulae.append(formula)
                        elif "integration check" in claim:
                            claim = claim.removeprefix("integration check")
                            formula = LTLParser().transform(self.ltlf_parser(claim))
                            self.device.integration_formulae.append(formula)
                        elif claim.startswith("subsystem"):
                            parts = claim.split(" ")  # separate by spaces
                            name = parts[1]  # get subystem name from formula
                            parts = parts[3:]  # remove 'subsystem XX check' from string
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
                                    for name, type in kw.value.items:
                                        self.device.components.create(
                                            name.value, type.value
                                        )
                                        self.device.uses = discover_uses(
                                            self.device.components
                                        )  # TODO: melhorar isto?

    def _process_if(self, node: astroid.NodeNG):
        # TODO: add support for choice with more than 2 branches
        # TODO: possibly merge this code with "_process_match_cases"?
        save_rule: TriggerRule = copy.copy(self.current_rule)
        self.current_rule = TriggerRuleFired()
        logger.debug("  If")
        for x in node.body:
            self.find(x)
        left_rule = copy.copy(self.current_rule)
        self.current_rule = TriggerRuleFired()
        logger.debug("  Else")
        for x in node.orelse:
            self.find(x)
        right_rule = copy.copy(self.current_rule)
        self.current_rule = save_rule
        branch_rule = TriggerRuleChoice()
        branch_rule.choices.extend([left_rule, right_rule])
        if not (
            isinstance(left_rule, TriggerRuleFired)
            and isinstance(right_rule, TriggerRuleFired)
        ):  # only proceed if 'ifelse' have calls inside
            match self.current_rule:
                case TriggerRuleFired():
                    self.current_rule = branch_rule
                case TriggerRule():  # any other type of rule
                    self.current_rule = TriggerRuleSequence(
                        self.current_rule, branch_rule
                    )

    def _process_match_cases(self, node_cases: List[astroid.MatchCase]):
        save_rule: TriggerRule = copy.copy(self.current_rule)
        for case in node_cases:
            logger.debug(f"    Match case: {case.pattern}")
            self.current_rule = save_rule
            self._return_check = False  # we must have a return for each match case
            for x in case.body:
                self.find(x)
            if not self._return_check:
                sys.exit(
                    f"PyShelley error\nExpecting return after line {x.lineno}. Did you forget the return statement in this case?"
                )

    def _process_call(self, node: astroid.NodeNG):
        subystem_call = node.func.attrname
        try:
            subystem_instance = node.func.expr.attrname
            exprself = node.func.expr.expr.name
            try:
                component: Component = self.device.components[subystem_instance]

                logger.debug(
                    f"    Call: {exprself}.{subystem_instance}.{subystem_call}"
                )
                match self.current_rule:
                    case TriggerRuleFired():
                        self.current_rule = TriggerRuleEvent(component, subystem_call)
                    case TriggerRule():  # any other type of rule
                        self.current_rule = TriggerRuleSequence(
                            self.current_rule,
                            TriggerRuleEvent(component, subystem_call),
                        )
            except KeyError as err:
                pass
                # TODO: make sure we handle invalid subsystems here
                # sys.exit(
                #     f"PyShelley error\nInvalid subsystem '{subystem_instance}' in '{subystem_instance}.{subystem_call}' on line {node.lineno}"
                # )

        except AttributeError:
            logger.debug(f"   Ignoring Call: {subystem_call}")

    def find(self, node):
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
                return self._process_decorators(node)
            case AnnAssign():
                self.find(node.value)
            case Expr():
                self.find(node.value)
            case Call():
                self._process_call(node)
            case Await():
                logger.debug(f"    Await")
                self.find(node.value)
            case Match():
                logger.debug(f"    Match")
                # self.print_call("Match", node.subject.value)
                self.find(node.subject)
                self._process_match_cases(node.cases)
            case Return():
                self._process_return(node)
                logger.debug(f"    Case return: {node.value.value}")
            case If():
                self._process_if(node)


def check(src_path: Path, uses_path: Path, output_path: Path):
    uses = parse_uses(uses_path)
    logger.debug(f"Uses: {uses}")

    with src_path.open() as f:
        tree = extract_node(f.read())

    # print(tree.repr_tree())

    svis = StrangeVisitor()
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

    # for x in svis.device.system_formulae:
    #     print(ltlf_lark_parser.dumps(x, nusvm_strict=False))
    #
    # for x in svis.device.integration_formulae:
    #     print(ltlf_lark_parser.dumps(x, nusvm_strict=False))