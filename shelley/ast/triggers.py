from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass, field

from shelley.ast.util import MyCollection
from shelley.ast.node import Node
from shelley.ast.rules import TriggerRule
from shelley.ast.events import GenericEvent

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


@dataclass(order=True)
class Trigger(Node):
    event: GenericEvent
    trigger_rule: TriggerRule = field(
        compare=False
    )  # do not use this field for comparing triggers

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """
        visitor.visit_trigger(self)

class TriggersListEmptyError(Exception):
    pass


class TriggersListDuplicatedError(Exception):
    pass


class TriggersEventUndeclaredError(Exception):
    pass


class TriggerRulesListEmptyError(Exception):
    pass


class Triggers(MyCollection[Trigger]):
    def create(self, event: GenericEvent, rule: TriggerRule) -> Trigger:
        trigger = Trigger(event, rule)
        if trigger not in self._data:
            self._data.append(trigger)
        else:
            raise TriggersListDuplicatedError()
        return trigger

    def get_rule(self, event_name: str) -> Optional[TriggerRule]:
        trigger: Optional[Trigger] = self.find_by_event(event_name)
        return trigger.trigger_rule if trigger is not None else None

    def find_by_event(self, event_name: str) -> Optional[Trigger]:
        re: Optional[Trigger] = None
        try:
            re = next(x for x in self._data if x.event.name == event_name)
        except StopIteration:
            pass
        return re

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_triggers(self)
