from __future__ import annotations
from abc import abstractmethod

from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from devices import Device

from ast.node import Node, Visitor
from ast.rules import TriggerRule
from events import EEvent


class Trigger(Node):
    event = None  # type: EEvent
    trigger_rule = None  # type: TriggerRule

    def __init__(self, event: EEvent, trigger_rule: TriggerRule):
        self.event = event
        self.trigger_rule = trigger_rule

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit(self)

    def check_event_is_declared(self, declared_e_events: List[EEvent]):
        if self.event not in declared_e_events:
            raise TriggersEventUndeclaredError(
                "Left event '{0}' must be declared in events section!".format(self.event.name))

    def check_is_duplicated(self, triggers_list: List[Trigger]):
        if self in triggers_list:
            raise TriggersListDuplicatedError(
                "Duplicated trigger with event '{0}'".format(self.event.name))

    def __eq__(self, other):
        if not isinstance(other, Trigger):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Trigger type")

        return self.event == other.event  # and self.device_name == other.device_name


class TriggersVisitor(Visitor):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """

    @abstractmethod
    def visit(self, element: Trigger) -> None:
        pass


class CheckWFSyntax(TriggersVisitor):
    triggers_list = None  # type: List[Trigger]
    declared_e_events = None  # type: List[EEvent]
    declared_components = None  # type: Dict[str, Device]

    def __init__(self, declared_e_events: List[EEvent], declared_components: Dict[str, Device]):
        self.triggers_list = []
        self.declared_e_events = declared_e_events
        self.declared_components = declared_components

    def visit(self, trigger: Trigger) -> None:
        trigger.check_event_is_declared(self.declared_e_events)
        trigger.check_is_duplicated(self.triggers_list)
        trigger.trigger_rule.accept(self)
        self.triggers_list.append(trigger)


class TriggersListEmptyError(Exception):
    pass


class TriggersListDuplicatedError(Exception):
    pass


class TriggersEventUndeclaredError(Exception):
    pass


class TriggerRulesListEmptyError(Exception):
    pass
