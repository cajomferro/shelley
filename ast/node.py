from __future__ import annotations
from abc import ABC, abstractmethod

from ast.triggers import Trigger
from ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent


class Node(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass


class Visitor(ABC):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """
    pass


class CheckWFSyntaxVisitor(Visitor):
    triggers_list = None  # type: List[Trigger]
    declared_e_events = None  # type: List[EEvent]
    declared_components = None  # type: Dict[str, Device]

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        element.check_wf_syntax(self.declared_components)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_trigger(self, element: Trigger) -> None:
        element.check_event_is_declared(self.declared_e_events)
        element.check_is_duplicated(self.triggers_list)
        element.trigger_rule.accept(self)
        self.triggers_list.append(element)
