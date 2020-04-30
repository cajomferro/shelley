from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass

from shelley.ast.util import MyCollection
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


class Actions(MyCollection[Action]):
    def create(self, action_name: str) -> Action:
        action = Action(action_name)
        if action not in self._data:
            self._data.append(action)
        else:
            raise ActionsListDuplicatedError()
        return action

    def __getitem__(self, name:str) -> Action:
        act = self.find_by_name(name)
        if act is None:
            raise KeyError(name)
        return act

    def find_by_name(self, name: str) -> Optional[Action]:
        # XXX: Use a dictionary to store values, not a list
        for x in self._data:
            if x.name == name:
                return x
        return None

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_actions(self)
