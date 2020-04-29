from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional, Tuple, Union
from dataclasses import dataclass

from shelley.ast.util import MyCollection
from shelley.ast.node import Node
from shelley.ast.events import GenericEvent
from shelley.ast.actions import Action

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


@dataclass(order=True)
class Behavior(Node):
    e1: GenericEvent
    e2: GenericEvent
    action: Optional[Action]

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_behaviour(self)

    def __str__(self):
        return (
            "{0} -> {1}".format(self.e1.name, self.e2.name)
            if self.action is None
            else "{0} -> {1}() {2}".format(self.e1.name, self.action.name, self.e2.name)
        )


class BehaviorMissingActionForInternalEvent(Exception):
    pass


class BehaviorUnexpectedActionForExternalEvent(Exception):
    pass


class BehaviorsListEmptyError(Exception):
    pass


class BehaviorEventUndeclared(Exception):
    pass


class BehaviorActionForInternalEventUndeclared(Exception):
    pass


class BehaviorsListDuplicatedError(Exception):
    pass


class BehaviorsMissingBegin(Exception):
    pass


class Behaviors(MyCollection[Behavior]):
    def create(
        self, e1: GenericEvent, e2: GenericEvent, a: Optional[Action] = None
    ) -> Behavior:
        behavior = Behavior(e1, e2, a)
        if behavior not in self._data:
            self._data.append(behavior)
        else:
            raise BehaviorsListDuplicatedError()
        return behavior

    def contains_events_pair(self, e1_name: str, e2_name: str) -> bool:
        return False if self.find_by_event_pair(e1_name, e2_name) is None else True

    def find_by_event_pair(self, e1_name: str, e2_name: str) -> Optional[Behavior]:
        re: Optional[Behavior] = None
        try:
            re = next(
                x for x in self._data if x.e1.name == e1_name and x.e2.name == e2_name
            )
        except StopIteration:
            pass
        return re

    def as_list_tuples(self,) -> List[Tuple[str, str]]:
        return [(str(elem.e1), str(elem.e2)) for elem in self.list()]

    def as_list_tuples_with_actions(self) -> List[Tuple[str, str, str]]:
        re = [(str(elem.e1), str(elem.action), str(elem.e2)) for elem in self.list()]
        return re

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_behaviors(self)
