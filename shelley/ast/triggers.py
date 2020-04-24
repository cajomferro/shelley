from __future__ import annotations
from typing import List, TYPE_CHECKING
from dataclasses import dataclass, field

from .util import MyCollection
from .node import Node
from .rules import TriggerRule
from .events import EEvent, GenericEvent

if TYPE_CHECKING:
    from .visitors import Visitor


@dataclass(order=True)
class Trigger(Node):
    event: GenericEvent
    trigger_rule: TriggerRule = field(compare=False)  # do not use this field for comparing triggers

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger(self)

    # def check(self, eevents: List[EEvent], triggers: List[Trigger]):
    #     self.check_event_is_declared(eevents)
    #     #self.check_is_duplicated(triggers)
    #     #triggers.append(self)
    #
    # def check_event_is_declared(self, eevents: List[EEvent]):
    #     if self.event not in eevents:
    #         raise TriggersEventUndeclaredError(
    #             "Left event '{0}' must be declared in events section!".format(self.event.name))

    # def check_is_duplicated(self, triggers: List[Trigger]):
    #     if self in triggers:
    #         raise TriggersListDuplicatedError(
    #             "Duplicated trigger with event '{0}'".format(self.event.name))

    # def __init__(self, event: EEvent, trigger_rule: TriggerRule):
    #     self.event = event
    #     self.trigger_rule = trigger_rule
    #
    # def __eq__(self, other):
    #     """
    #     Triggers are equal if the event name is the same
    #     :param other:
    #     :return:
    #     """
    #     if not isinstance(other, Trigger):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance is not of Trigger type")
    #
    #     return self.event.name == other.event.name


class TriggersListEmptyError(Exception):
    pass


class TriggersListDuplicatedError(Exception):
    pass


class TriggersEventUndeclaredError(Exception):
    pass


class TriggerRulesListEmptyError(Exception):
    pass


class Triggers(Node, MyCollection[Trigger]):
    _data = None  # type: List[Trigger]

    def __init__(self):
        self._data = list()

    def create(self, event: GenericEvent, rule: TriggerRule) -> Trigger:
        trigger = Trigger(event, rule)
        if trigger not in self._data:
            self._data.append(trigger)
        else:
            raise TriggersListDuplicatedError()
        return trigger

    def get_rule(self, event_name) -> TriggerRule:
        return self.find_by_event(event_name).trigger_rule

    def find_by_event(self, event_name: str) -> Trigger:
        re: Trigger
        try:
            re = next(x for x in self._data if x.event.name == event_name)
        except StopIteration:
            pass
        return re

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_triggers(self)
