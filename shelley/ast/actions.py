from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from dataclasses import dataclass

from shelley.ast.node import Node

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


@dataclass(order=True)
class Action(Node):
    name: str

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_action(self)

    def __str__(self):
        return self.name


class ActionsListEmptyError(Exception):
    pass


class ActionsListDuplicatedError(Exception):
    pass


class Actions(Node):
    _data: List[Action]

    def __init__(self) -> None:
        self._data = []

    def add(self, elem: Action) -> None:
        if elem not in self._data:
            self._data.append(elem)
        else:
            raise ActionsListDuplicatedError()

    def contains(self, elem: Action) -> bool:
        return elem in self._data

    def list(self) -> List[Action]:
        return self._data

    def list_str(self) -> List[str]:
        return [str(elem) for elem in self._data]

    def __len__(self):
        return len(self._data)

    def create(self, action_name: str) -> Action:
        action = Action(action_name)
        if action not in self._data:
            self._data.append(action)
        else:
            raise ActionsListDuplicatedError()
        return action

    def find_by_name(self, name: str) -> Optional[Action]:
        # XXX: This should be the standard method: get
        for x in self._data:
            if x.name == name:
                return x
        return None

    def __getitem__(self, name: str) -> Action:
        res = self.find_by_name(name)
        if res is None:
            raise KeyError(name)
        return res

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_actions(self)
