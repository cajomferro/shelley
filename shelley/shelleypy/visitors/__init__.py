import copy
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List

from astroid import (
    Call,
    MatchCase,
    FunctionDef,
    NodeNG
)

from shelley.ast.behaviors import Behaviors
from shelley.ast.components import Components
from shelley.ast.devices import Device
from shelley.ast.events import Event
from shelley.ast.events import Events
from shelley.ast.rules import (
    TriggerRuleFired,
)
from shelley.ast.triggers import TriggerRule
from shelley.ast.triggers import Triggers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


class ShelleyPyError(Exception):
    MISSING_RETURN = "Missing return!"
    CASE_MISSING_RETURN = "Missing return for case!"
    IF_ELSE_MISSING_RETURN = "One of the if/else branches has return and the other not!"
    MATCH_CALL_TYPE = "Match call type mismatch. Accepted types are: Call, Await!"
    MATCH_CASE_VALUE_TYPE = "Cases values must be strings!"

    def __init__(self, lineno: int, msg: str):
        self.lineno = lineno
        self.msg = msg
        super().__init__(self.msg)


@dataclass
class ShelleyCall:
    node_call: Call

    def get_exprself(self) -> str:
        return self.node_call.func.expr.expr.name

    def get_subsystem_call(self) -> str:
        return self.node_call.func.attrname

    def get_subsystem_instance(self) -> str:
        return self.node_call.func.expr.attrname

    def __str__(self):
        return f"{self.get_exprself()}.{self.get_subsystem_instance()}.{self.get_subsystem_call()}"


@dataclass
class VisitorHelper:
    device: Device = Device(
        name="",
        events=Events(),
        behaviors=Behaviors(),
        triggers=Triggers(),
        components=Components(),
    )
    external_only: bool = False
    match_found: bool = False  # useful for verifying missing returns
    current_rule: TriggerRule = TriggerRuleFired()
    last_current_rule_saved: Optional[TriggerRule] = None
    current_match_call: Optional[ShelleyCall] = None
    saved_case_rules: List[TriggerRule] = field(default_factory=list)
    saved_operations = list()
    last_call: Optional[ShelleyCall] = None
    n_returns: int = 0

    def check_case_first_node(self, case_name: str, matchcase_body_node: NodeNG):
        # inspect first expression inside case body
        expected_call_name = f"{self.current_match_call.get_exprself()}.{self.current_match_call.get_subsystem_instance()}.{case_name}"
        if not (self.last_call and str(self.last_call) == expected_call_name):
            logger.warning(
                f"Expecting {expected_call_name} but found {self.last_call}. The first subsystem call should match the case name! (l. {matchcase_body_node.lineno})")

    def get_case_name(self, match_case_node: MatchCase):
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

    def is_base_system(self):
        return len(self.device.uses) == 0 or self.external_only

    def create_operation(self, name, is_initial, is_final, next_ops_list, rules):
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
