from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List

from astroid import (
    For,
    Await,
    Call,
    Return,
    Expr,
    If,
    Match,
    MatchValue,
    MatchCase,
    FunctionDef,
    NodeNG
)

from shelley.ast.components import Component
from shelley.ast.devices import Device
from shelley.ast.events import Event
from shelley.ast.rules import (
    TriggerRuleSequence,
    TriggerRuleEvent,
    TriggerRuleFired,
)
from shelley.ast.triggers import TriggerRule
from shelley.shelleypy.visitors import ShelleyPyError
from shelley.shelleypy.visitors.method_decorators import MethodDecoratorsVisitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


# @dataclass
# class CallVisitor(NodeNG):
#     call_node: NodeNG = None
#     subystem_call: str = None
#     subystem_instance: str = None
#     exprself: str = None
#
#     def visit_call(self, node: Call):
#         logger.debug(node)
#         try:
#             self.call_node = node
#             self.subystem_call = node.func.attrname
#             self.subystem_instance = node.func.expr.attrname
#             self.exprself = node.func.expr.expr.name
#
#             logger.debug("Call name: %s", call_name)
#         except AttributeError:
#             logger.debug(f"    Ignoring Call: {node.func.repr_tree()}")
#             return
#
#     def visit_await(self, node: Await):
#         logger.debug(node)
#         # TODO:


@dataclass
class CaseNameVisitor(NodeNG):
    def visit_matchsequence(self, node: MatchValue):
        raise ShelleyPyError(node.lineno, ShelleyPyError.LIST_CASE)

    def visit_matchvalue(self, node: MatchValue):
        logger.debug(node)
        return node.value.value


@dataclass
class ShelleyCall:
    node_call: Call

    def get_subsystem_call(self) -> str:
        return self.node_call.func.attrname

    def get_subsystem_instance(self) -> str:
        return self.node_call.func.expr.attrname

    def __str__(self):
        exprself = self.node_call.func.expr.expr.name
        return f"{exprself}.{self.get_subsystem_instance()}.{self.get_subsystem_call()}"


@dataclass
class MethodVisitor(NodeNG):
    device: Device
    external_only: bool = False
    match_found: bool = False  # useful for verifying missing returns
    current_rule: TriggerRule = TriggerRuleFired()
    last_current_rule_saved: Optional[TriggerRule] = None
    current_match_call: Optional[str] = None
    saved_case_rules: List[TriggerRule] = field(default_factory=list)
    saved_operations = list()
    last_call: Optional[ShelleyCall] = None
    n_returns: int = 0

    def visit_functiondef(self, node: FunctionDef) -> Any:
        logger.info(f"Method: {node.name}")
        logger.debug(node)
        decorator = self._get_decorator(node.decorators)

        if decorator:
            self._process_operation(node, decorator)

    def visit_match(self, node: Match):
        logger.debug(node)
        self.match_found = True

        node.subject.accept(self)

        if not isinstance(self.last_call.node_call, Call):
            raise ShelleyPyError(node.subject.lineno, ShelleyPyError.MATCH_CALL_TYPE)

        for node_case in node.cases:
            node_case.accept(self)

        self.reset_current_rule()

    def visit_matchcase(self, match_case_node: MatchCase):
        logger.debug(match_case_node)

        # retrieve case name
        case_name: str = match_case_node.pattern.accept(CaseNameVisitor())  # -> visit_matchvalue

        # match_exprself, match_subystem_instance, _ = self.current_match_call.split(".")

        self.save_current_rule()
        self.returns_reset()  # start counting returns, we must have a return for each match case

        # inspect case body
        for matchcase_body_node in match_case_node.body:
            matchcase_body_node.accept(self)

        self.save_current_case_rule()
        self.restore_current_rule()

        if not self.n_returns:
            raise ShelleyPyError(match_case_node.lineno, ShelleyPyError.CASE_MISSING_RETURN)

    def visit_await(self, node: Await):
        logger.debug(node)
        node.value.accept(self)

    def visit_call(self, node: Call):
        logger.debug(node)

        try:
            self.last_call = ShelleyCall(node)
        except AttributeError:
            logger.debug(f"    Ignoring Call: {node.func.repr_tree()}")
            return

        try:
            component: Component = self.device.components[self.last_call.get_subsystem_instance()]
        except KeyError:
            logger.debug(f"    Ignoring Call: {self.last_call}")
            return

        match self.current_rule:
            case TriggerRuleFired():
                self.current_rule = TriggerRuleEvent(component, self.last_call.get_subsystem_call())
            case TriggerRule():  # any other type of rule
                self.current_rule = TriggerRuleSequence(
                    self.current_rule,
                    TriggerRuleEvent(component, self.last_call.get_subsystem_call()),
                )

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

    def visit_expr(self, node: Expr):
        logger.debug(node)

    def visit_return(self, node: Return):
        logger.debug(node)

    def returns_reset(self):
        self.n_returns = 0

    def returns_increment(self):
        self.n_returns += 1

    def returns_count(self):
        return self.n_returns

    def save_current_case_rule(self):
        self.saved_case_rules.append(self.current_rule)

    def save_current_rule(self):
        self.last_current_rule_saved = copy.copy(self.current_rule)

    def reset_current_rule(self):
        self.current_rule = TriggerRuleFired()

    def restore_current_rule(self):
        self.current_rule = self.last_current_rule_saved
        self.last_current_rule_saved = None

    def _process_operation(self, node: FunctionDef, decorator: Dict):
        if (
                len(self.device.uses) == 0
        ) or self.external_only:  # base system, do not inspect body
            self._create_operation(
                node.name,
                decorator["initial"],
                decorator["final"],
                decorator["next"],
                TriggerRuleFired(),
            )
        else:  # system that contains subsystems, do inspect body
            assert type(node) == FunctionDef  # this is just a safe check
            for node in node.body:
                node.accept(self)

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

    @staticmethod
    def _get_decorator(decorators):
        if decorators is None:
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        decorators_visitor = MethodDecoratorsVisitor()
        decorators.accept(decorators_visitor)
        decorator = decorators_visitor.decorator

        if decorator is None:
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        if not decorator["type"] == "operation":
            logger.debug(f"Skipping. This method is not annotated as an operation!")
            return None

        return decorator
