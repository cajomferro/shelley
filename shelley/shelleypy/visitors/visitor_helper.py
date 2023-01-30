import copy
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, Union

from lark import Lark

from astroid import NodeNG

from shelley.ast.behaviors import Behaviors
from shelley.ast.components import Components, Component
from shelley.ast.devices import Device, discover_uses
from shelley.ast.events import Event
from shelley.ast.events import Events
from shelley.ast.rules import (
    TriggerRuleEvent,
    TriggerRuleSequence,
    TriggerRuleChoice,
    TriggerRuleFired,
    TriggerRuleLoop,
)
from shelley.ast.triggers import TriggerRule
from shelley.ast.triggers import Triggers
from shelley.parsers import ltlf_lark_parser
from shelley.parsers.ltlf_lark_parser import LTLParser
from shelley.shelleypy.checker.exceptions import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")

TriggerRuleBranch = Union[TriggerRuleChoice, TriggerRuleLoop, TriggerRuleFired]


class ContextTypes:
    DEFAULT = 0
    BRANCH = 1
    LOOP = 2


@dataclass
class ReturnPath:
    return_next: List[str]
    lineno: int
    path: TriggerRule


@dataclass
class Context:
    parent_context: Any
    node: NodeNG
    current_path: Optional[TriggerRule] = None
    return_paths: List[ReturnPath] = field(default_factory=list)
    branch_path: TriggerRuleBranch = None

    def __post_init__(self):
        self.branch_path = TriggerRuleChoice()

    def return_path_put(self, return_next: List[str], lineno: int):
        logger.debug(f"[{self.node.lineno}] Found return: {return_next}")
        if not self.current_path:
            self.current_path = TriggerRuleFired()
        return_path = ReturnPath(return_next, lineno, self.current_path)
        logger.debug(f"[{self.node.lineno}] Return paths put: {return_path.path}")
        self.return_paths.append(return_path)
        # print(
        #     f"[{self.node.lineno}] Return paths: {[str(returnp.path) for returnp in self.return_paths]}"
        # )
        self.current_path = None

    def return_path_update(self, suffix_rpath: ReturnPath):
        # logger.debug(f"[{self.node.lineno}] Return paths update:")
        if self.current_path is not None:
            suffix_rpath.path = TriggerRuleSequence(
                self.current_path, suffix_rpath.path
            )
        self.return_paths.append(suffix_rpath)
        # logger.debug(f"[{self.node.lineno}] Return paths: {[str(returnp.path) for returnp in self.return_paths]}")

    def current_path_update(self, rule: Optional[TriggerRule] = None):
        self.current_path = rule
        logger.debug(f"[{self.node.lineno}]Current path updated: {self.current_path}")

    def current_path_merge(self):
        # logger.info("Adding branch")
        if self.current_path:
            rule = TriggerRuleSequence(self.current_path, self.branch_path)
        else:
            rule = self.branch_path
        self.current_path_update(rule)

    def end(self):
        pass


@dataclass
class BranchContext(
    Context
):  # TODO: should I have different context types that inherit from a generic one?
    def end(self):
        """
        order matters!
        """
        # update parent with all my returns
        for rpath in self.return_paths:
            self.parent_context.return_path_update(rpath)

        # update parent branch path with my current path
        if self.current_path:
            self.parent_context.branch_path.add_choice(self.current_path)

@dataclass
class LoopContext(
    Context
):  # TODO: should I have different context types that inherit from a generic one?
    def end(self):
        # update parent branch path with my current path
        if self.current_path:
            loop_rule = TriggerRuleLoop(self.current_path)
            self.current_path_update(loop_rule)
            self.parent_context.branch_path.add_choice(self.current_path)

        # update parent with all my returns
        for rpath in self.return_paths:
            if self.current_path:
                rpath.path = TriggerRuleSequence(self.current_path, rpath.path)
            self.parent_context.return_path_update(rpath)


@dataclass
class ShelleyCall:
    exprself: str
    subsystem_call: str
    subsystem_instance: str

    def __str__(self):
        return f"{self.exprself}.{self.subsystem_instance}.{self.subsystem_call}"


@dataclass
class ShelleyOpDecorator:
    op_name: str
    is_initial: bool = False
    is_final: bool = False
    next_ops: List[str] = field(default_factory=list)


@dataclass
class VisitorHelper:
    device: Device = field(init=False)
    external_only: bool = False
    branch_contexts: List[Context] = field(default_factory=list)
    match_found: bool = False  # useful for verifying missing returns
    current_match_call: Optional[
        ShelleyCall
    ] = None  # useful for checking that the first match case matches the subsystem of the match call
    last_call: Optional[ShelleyCall] = None
    n_returns: int = 0  # TODO: this is probably outdated
    current_op_decorator: ShelleyOpDecorator = None
    current_return_op_name: Optional[str] = None
    collect_extra_ops: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.device = Device(
            name="",
            events=Events(),
            behaviors=Behaviors(),
            triggers=Triggers(),
            components=Components(),
        )

    def check_case_first_node(self, case_name: str, lineno: int):
        # inspect first expression inside case body
        expected_call_name = f"{self.current_match_call.exprself}.{self.current_match_call.subsystem_instance}.{case_name}"
        if not (self.last_call and str(self.last_call) == expected_call_name):
            logger.warning(
                f"Expecting {expected_call_name} but found {self.last_call}. The first subsystem call should match the case name! (l. {lineno})"
            )

    def context_system_init(
        self,
        name: str,
        uses: Dict[str, str],
        system_claims: List[str],
        integration_claims: List[str],
        subsystem_claims: List[str],
    ):
        self.device.name = name

        for c_name, c_type in uses.items():
            self.device.components.create(c_name, c_type)
        self.device.uses = discover_uses(self.device.components)

        ltlf_parser = Lark.open(
            "ltlf_grammar.lark", rel_to=ltlf_lark_parser.__file__, start="formula"
        ).parse

        for claim in system_claims:
            formula = LTLParser().transform(ltlf_parser(claim))
            self.device.system_formulae.append(formula)

        for claim in integration_claims:
            formula = LTLParser().transform(ltlf_parser(claim))
            self.device.integration_formulae.append(formula)

        for subsystem_name, claim in subsystem_claims:
            formula = LTLParser().transform(ltlf_parser(claim))
            self.device.subsystem_formulae.append((subsystem_name, formula))

    def context_operation_init(self, decorator: ShelleyOpDecorator):
        # self.current_path_clear()
        self.collect_extra_ops = dict()
        self.current_op_decorator = decorator
        self.n_returns = 0
        self.match_found = False
        self.current_return_op_name = None

    def context_operation_end(self, lineno: int):
        op_name = self.current_op_decorator.op_name
        is_initial = self.current_op_decorator.is_initial
        is_final = self.current_op_decorator.is_final
        next_ops = self.current_op_decorator.next_ops

        missing_returns: Set[str] = set(next_ops) - self._original_return_names()
        if missing_returns:
            raise NextOpsNotInReturn(lineno, missing_returns)

        # for single-return methods, use the name of the method
        if len(self.collect_extra_ops) == 1:
            self.register_new_operation(
                op_name=op_name,
                is_initial=is_initial,
                is_final=is_final,
                next_ops=next_ops,
                rules=self.collect_extra_ops[self.current_return_op_name]["rules"],
            )
        else:  # for multiple-return methods, use the name of the extra operations...
            for extra_op_name, extra_op_info in self.collect_extra_ops.items():
                self.register_new_operation(
                    op_name=extra_op_name,
                    is_initial=False,
                    is_final=is_final,
                    next_ops=extra_op_info["next"],
                    rules=extra_op_info["rules"],
                )

            # ... and map the original operation with the extra operations
            next_ops = [
                extra_op_name for extra_op_name in self.collect_extra_ops.keys()
            ]
            self.register_new_operation(
                op_name=op_name,
                is_initial=is_initial,
                is_final=False,
                next_ops=next_ops,
            )

        if not self.match_found and self.n_returns == 0:
            raise ShelleyPyError(lineno, ShelleyPyError.MISSING_RETURN)

    def _original_return_names(self) -> Set[str]:
        return_names_set = set()
        for _, v in self.collect_extra_ops.items():
            for return_name in v["original_return_names"]:
                return_names_set.add(return_name)
        return return_names_set

    def register_new_operation(
        self,
        op_name: str,
        is_initial=False,
        is_final=False,
        next_ops: Optional[List[str]] = None,
        rules: Optional[TriggerRule] = None,
    ):

        if next_ops is None:
            next_ops = []

        if rules is None:
            rules = TriggerRuleFired()

        current_operation: Event = self.device.events.create(
            op_name, is_start=is_initial, is_final=is_final
        )

        if len(next_ops) == 0:
            self.device.behaviors.create(
                copy.copy(current_operation)
            )  # operation without next operations
        else:
            for next_op in next_ops:
                self.device.behaviors.create(
                    copy.copy(current_operation),
                    Event(
                        name=next_op,
                        is_start=False,
                        is_final=True,
                    ),
                )

        self.device.triggers.create(copy.copy(current_operation), copy.copy(rules))

    def register_new_call(self):
        try:
            component: Component = self.device.components[
                self.last_call.subsystem_instance
            ]
        except KeyError:
            logger.debug(f"    Ignoring Call: {self.last_call}")
            return

        if self.current_path() is None:
            self.current_context().current_path_update(
                TriggerRuleEvent(component, self.last_call.subsystem_call)
            )
        else:
            self.current_context().current_path_update(
                TriggerRuleSequence(
                    self.current_path(),
                    TriggerRuleEvent(component, self.last_call.subsystem_call),
                )
            )

    def register_new_return(self, return_path: ReturnPath):
        # TODO: create a visitor to find the leftmost rule and then, if not None, use that name for the return, else use the index
        self.current_return_op_name: str = (
            f"{self.current_op_decorator.op_name}_{len(self.collect_extra_ops) + 1}"
        )
        logger.debug(f"Registered next operation name: {self.current_return_op_name}")

        self.collect_extra_ops[self.current_return_op_name] = {
            "next": return_path.return_next,
            "rules": return_path.path,
            "original_return_names": return_path.return_next,
        }
        # logger.debug(f"Collect extra ops: {self.collect_extra_ops}")
        # logger.debug(f"Current rule: {self.current_path()}")

        next_ops_list = self.current_op_decorator.next_ops
        if next_ops_list and not all(
            elem in next_ops_list for elem in return_path.return_next
        ):
            raise ReturnMatchesNext(return_path.lineno, return_path.return_next)
        if not next_ops_list and return_path.return_next != [""]:
            raise ReturnMatchesNext(return_path.lineno, return_path.return_next)

        self.n_returns += 1

    def is_base_system(self):
        return len(self.device.uses) == 0 or self.external_only

    def set_match_call_to_last_call(self):
        # logger.debug("Match call copied")
        self.current_match_call = self.last_call

    def copy_match_call(self):
        # logger.debug("Match call saved")
        return copy.copy(self.current_match_call)

    def restore_match_call(self, saved_match_call):
        # logger.debug("Match call restored")
        self.current_match_call = saved_match_call

    def context_init(self, node, type=ContextTypes.DEFAULT):
        # logger.debug(f"New context: {node}")
        match type:
            case ContextTypes.BRANCH:
                ctx = BranchContext(parent_context=self.current_context(), node=node)
            case ContextTypes.LOOP:
                ctx = LoopContext(parent_context=self.current_context(), node=node)
            case _:
                ctx = Context(parent_context=self.current_context(), node=node)
        self.branch_contexts.append(ctx)
        return ctx

    def context_end(self):
        self.current_context().end()
        return self.branch_contexts.pop()

    def current_context(self):
        return self.branch_contexts[-1] if len(self.branch_contexts) else None

    def current_path(self) -> TriggerRule:
        return self.current_context().current_path if self.current_context() else None

    def register_return_paths(self):
        logger.debug("Registering return paths")
        for return_path in self.current_context().return_paths:
            # print(return_path.path)
            self.register_new_return(return_path)
