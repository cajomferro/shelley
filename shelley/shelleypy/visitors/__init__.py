import copy
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any

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
    RETURN_PARSE_ERROR = "Could not parse return. Expecting str|list[,*]"
    DECORATOR_PARSE_ERROR = "Could not parse decorator!"

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
class ShelleyOpDecorator:
    op_name: str
    is_initial: bool = False
    is_final: bool = False
    next: List[str] = field(default_factory=list)


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
    current_op_decorator: ShelleyOpDecorator = None
    method_return_idx: int = 0
    current_return_op_name: str = None
    collect_extra_ops: Dict[str, Any] = field(default_factory=dict)

    def check_case_first_node(self, case_name: str, matchcase_body_node: NodeNG):
        # inspect first expression inside case body
        expected_call_name = f"{self.current_match_call.get_exprself()}.{self.current_match_call.get_subsystem_instance()}.{case_name}"
        if not (self.last_call and str(self.last_call) == expected_call_name):
            logger.warning(
                f"Expecting {expected_call_name} but found {self.last_call}. The first subsystem call should match the case name! (l. {matchcase_body_node.lineno})")

    def context_operation_init(self, decorator: ShelleyOpDecorator):
        self.current_op_decorator = decorator
        self.n_returns = 0
        self.method_return_idx = 0
        self.match_found = False
        self.saved_case_rules = []
        self.curent_return_op_name = None

    def context_match_init(self):
        self.match_found = True

    def context_match_end(self):
        #self.match_found = False?
        self.current_rule = TriggerRuleFired()

    def context_match_case_init(self):
        self._save_current_rule()
        self.n_returns = 0  # start counting returns, we must have a return for each match case

    def context_match_case_end(self):
        self.saved_case_rules.append(self.current_rule)
        self._restore_current_rule()

    def reset_for_context(self):
        self._save_current_rule()

    def register_new_return(self, return_next: List[str]) -> bool:
        # TODO: create a visitor to find the leftmost rule and then, if not None, use that name for the return, else use the index
        self.current_return_op_name: str = (
            f"{self.current_op_decorator.op_name}_{self.method_return_idx}"
        )
        logger.debug(f" Registered new return operation name: {self.current_return_op_name}")
        self.saved_operations.append(self.curent_return_op_name)
        self.collect_extra_ops[self.current_return_op_name] = {
            "next": return_next,
            "rules": self.current_rule,
        }

        next_ops_list = self.current_op_decorator.next
        if next_ops_list and not all(elem in next_ops_list for elem in return_next):
            return False
        if not next_ops_list and return_next != [""]:
            return False

        self.n_returns += 1

        return True

    def _save_current_rule(self):
        self.last_current_rule_saved = copy.copy(self.current_rule)

    def _restore_current_rule(self):
        self.current_rule = self.last_current_rule_saved
        self.last_current_rule_saved = None

    def is_base_system(self):
        return len(self.device.uses) == 0 or self.external_only

    def create_operation(self, name, rules):
        decorator = self.current_op_decorator

        current_operation: Event = self.device.events.create(name, is_start=decorator.is_initial,
                                                             is_final=decorator.is_final)

        if len(decorator.next) == 0:
            self.device.behaviors.create(copy.copy(current_operation))  # operation without next operations

        for next_op in decorator.next:
            self.device.behaviors.create(
                copy.copy(current_operation),
                Event(name=next_op, is_start=False, is_final=True, ),
            )

        self.device.triggers.create(copy.copy(current_operation), copy.copy(rules))
