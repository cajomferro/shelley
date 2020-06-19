from __future__ import annotations
from typing import List, TYPE_CHECKING, Optional, Tuple, Union
from dataclasses import dataclass

from shelley.ast.node import Node
from shelley.ast.events import Event
from shelley.ast.actions import Action

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


@dataclass(order=True)
class Behavior(Node):
    e1: Event
    e2: Event
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


class Behaviors(Node):
    _data: List[Behavior]

    def __init__(self) -> None:
        self._data = []

    def __eq__(self, other):
        return (
            other is not None
            and isinstance(other, Behaviors)
            and set(self._data) == set(other._data)
        )

    def add(self, elem: Behavior) -> None:
        if elem not in self._data:
            self._data.append(elem)
        else:
            raise BehaviorsListDuplicatedError()

    def contains(self, elem: Behavior) -> bool:
        return elem in self._data

    def list(self) -> List[Behavior]:
        return self._data

    def list_str(self) -> List[str]:
        return [str(elem) for elem in self._data]

    def __len__(self):
        return len(self._data)

    def create(self, e1: Event, e2: Event, a: Optional[Action] = None) -> Behavior:
        behavior = Behavior(e1, e2, a)
        if behavior not in self._data:
            self._data.append(behavior)
        else:
            raise BehaviorsListDuplicatedError(str(behavior))
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
