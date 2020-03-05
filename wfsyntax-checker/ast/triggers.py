from __future__ import annotations
from typing import List, TYPE_CHECKING

from ast.node import Node
from ast.rules import TriggerRule
from ast.events import EEvent

if TYPE_CHECKING:
    from ast.visitors import Visitor


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

        visitor.visit_trigger(self)

    def check(self, eevents: List[EEvent], triggers: List[Trigger]):
        self.check_event_is_declared(eevents)
        self.check_is_duplicated(triggers)
        triggers.append(self)

    def check_event_is_declared(self, eevents: List[EEvent]):
        if self.event not in eevents:
            raise TriggersEventUndeclaredError(
                "Left event '{0}' must be declared in events section!".format(self.event.name))

    def check_is_duplicated(self, triggers: List[Trigger]):
        if self in triggers:
            raise TriggersListDuplicatedError(
                "Duplicated trigger with event '{0}'".format(self.event.name))

    def __eq__(self, other):
        if not isinstance(other, Trigger):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Trigger type")

        return self.event == other.event  # and self.device_name == other.device_name


class TriggersListEmptyError(Exception):
    pass


class TriggersListDuplicatedError(Exception):
    pass


class TriggersEventUndeclaredError(Exception):
    pass


class TriggerRulesListEmptyError(Exception):
    pass
