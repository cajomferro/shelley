import copy
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any

from astroid import (
    Call
)
from lark import Lark

from shelley.ast.behaviors import Behaviors
from shelley.ast.components import Components, Component
from shelley.ast.devices import Device, discover_uses
from shelley.ast.events import Event
from shelley.ast.events import Events
from shelley.ast.rules import (
    TriggerRuleEvent,
    TriggerRuleSequence,
    TriggerRuleFired,
    TriggerRuleLoop,
)
from shelley.ast.triggers import TriggerRule
from shelley.ast.triggers import Triggers
from shelley.parsers import ltlf_lark_parser
from shelley.parsers.ltlf_lark_parser import LTLParser

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
    next_ops: List[str] = field(default_factory=list)


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
    current_return_op_name: Optional[str] = None
    collect_extra_ops: Dict[str, Any] = field(default_factory=dict)

    def check_case_first_node(self, case_name: str, lineno: int):
        # inspect first expression inside case body
        expected_call_name = f"{self.current_match_call.get_exprself()}.{self.current_match_call.get_subsystem_instance()}.{case_name}"
        if not (self.last_call and str(self.last_call) == expected_call_name):
            logger.warning(
                f"Expecting {expected_call_name} but found {self.last_call}. The first subsystem call should match the case name! (l. {lineno})")

    def context_system_init(self, name: str, uses: Dict[str, str], system_claims: List[str],
                            integration_claims: List[str], subsystem_claims: List[str]):
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

        for claim in subsystem_claims:
            formula = LTLParser().transform(ltlf_parser(claim))
            self.device.subsystem_formulae.append((name, formula))

    def context_operation_init(self, decorator: ShelleyOpDecorator):
        self.current_op_decorator = decorator
        self.n_returns = 0
        self.method_return_idx = 0
        self.match_found = False
        self.saved_case_rules = []
        self.current_return_op_name = None

    def context_operation_end(self):
        op_name = self.current_op_decorator.op_name
        is_initial = self.current_op_decorator.is_initial
        is_final = self.current_op_decorator.is_final
        next_ops = self.current_op_decorator.next_ops

        for case_rule in self.saved_case_rules:
            self.collect_extra_ops[self.current_return_op_name].update(
                {"rules": TriggerRuleSequence(self.current_rule, case_rule)}
            )

        # for single-return methods, use the name of the method
        if len(self.collect_extra_ops) == 1:
            self.register_new_operation(op_name=op_name, is_initial=is_initial, is_final=is_final,
                                        next_ops=next_ops,
                                        rules=self.collect_extra_ops[self.current_return_op_name]["rules"])
        else:  # for multiple-return methods, use the name of the extra operations...
            for extra_op_name, extra_op_info in self.collect_extra_ops.items():
                self.register_new_operation(op_name=extra_op_name, is_initial=False, is_final=is_final,
                                            next_ops=extra_op_info["next"], rules=extra_op_info["rules"])

            # ... and map the original operation with the extra operations
            next_ops = [extra_op_name for extra_op_name in self.collect_extra_ops.keys()]
            self.register_new_operation(op_name=op_name, is_initial=is_initial, is_final=False,
                                        next_ops=next_ops)

        if not self.match_found and self.n_returns == 0:
            return False

        self.collect_extra_ops = dict()
        self.current_rule = TriggerRuleFired()
        self.saved_operations = list()

        return True

    def context_match_init(self):
        self.match_found = True

    def context_match_end(self):
        # self.match_found = False?
        self.current_rule = TriggerRuleFired()

    def context_match_case_init(self):
        self._save_current_rule()
        self.n_returns = 0  # start counting returns, we must have a return for each match case

    def context_match_case_end(self):
        self.saved_case_rules.append(self.current_rule)
        self._restore_current_rule()

    def context_for_init(self):
        self._save_current_rule()

    def register_new_operation(self, op_name: str, is_initial=False, is_final=False,
                               next_ops: Optional[List[str]] = None, rules: Optional[TriggerRule] = None):

        if next_ops is None:
            next_ops = []

        if rules is None:
            rules = TriggerRuleFired()

        current_operation: Event = self.device.events.create(op_name, is_start=is_initial, is_final=is_final)

        if len(next_ops) == 0:
            self.device.behaviors.create(copy.copy(current_operation))  # operation without next operations
        else:
            for next_op in next_ops:
                self.device.behaviors.create(
                    copy.copy(current_operation),
                    Event(name=next_op, is_start=False, is_final=True, ),
                )

        self.device.triggers.create(copy.copy(current_operation), copy.copy(rules))

    def register_new_for(self):
        loop_rule = TriggerRuleLoop(self.current_rule)
        self.current_rule = TriggerRuleSequence(self.last_current_rule_saved, loop_rule)

    def register_new_call(self):
        try:
            component: Component = self.device.components[
                self.last_call.get_subsystem_instance()]
        except KeyError:
            logger.debug(f"    Ignoring Call: {self.last_call}")
            return

        match self.current_rule:
            case TriggerRuleFired():
                self.current_rule = TriggerRuleEvent(component,
                                                     self.last_call.get_subsystem_call())
            case TriggerRule():  # any other type of rule
                self.current_rule = TriggerRuleSequence(
                    self.current_rule,
                    TriggerRuleEvent(component, self.last_call.get_subsystem_call()),
                )

    def register_new_return(self, return_next: List[str]) -> bool:
        # TODO: create a visitor to find the leftmost rule and then, if not None, use that name for the return, else use the index
        self.current_return_op_name: str = (
            f"{self.current_op_decorator.op_name}_{self.method_return_idx}"
        )
        logger.debug(f" Registered new return operation name: {self.current_return_op_name}")
        self.saved_operations.append(self.current_return_op_name)
        self.collect_extra_ops[self.current_return_op_name] = {
            "next": return_next,
            "rules": self.current_rule,
        }

        next_ops_list = self.current_op_decorator.next_ops
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
