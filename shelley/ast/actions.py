from __future__ import annotations
from typing import Set, TYPE_CHECKING
from dataclasses import dataclass

from .util import MyCollection
from .node import Node

if TYPE_CHECKING:
    from ast.visitors import Visitor


@dataclass(order=True)
class Action(Node):
    name: str

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_action(self)

    def check(self, actions: Set[Action]):
        self.check_is_duplicated(actions)
        actions.append(self)

    def __str__(self):
        return self.name

    # def check_is_duplicated(self, actions: Set[Action]):
    #     if self in actions:
    #         raise ActionsListDuplicatedError("Duplicated action: {0}".format(self.name))

    # def __new__(cls, name: str):
    #     instance = find_instance_by_name(name, actions)
    #     if instance is None:
    #         instance = super(Action, cls).__new__(cls)
    #         actions.append(instance)
    #     return instance

    # def __eq__(self, other):
    #     if not isinstance(other, Action):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance is not of Action type")
    #
    #     return self.name == other.name
    #
    # # https://docs.python.org/3.1/reference/datamodel.html?highlight=hash#object.__hash__
    # # https://stackoverflow.com/questions/1608842/types-that-define-eq-are-unhashable
    # # https://stackoverflow.com/questions/8705378/pythons-in-set-operator
    # def __hash__(self):
    #     return id(self.uuid)


class ActionsListEmptyError(Exception):
    pass


class ActionsListDuplicatedError(Exception):
    pass


class Actions(Node, MyCollection[Action]):

    def create(self, action_name: str) -> Action:
        action = Action(action_name)
        if action not in self._data:
            self._data.append(action)
        else:
            raise ActionsListDuplicatedError()
        return action

    def find_by_name(self, name: str) -> Action:
        re = None  # type: Action
        try:
            re = next(x for x in self._data if x.name == name)
        except StopIteration:
            pass
        return re

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_actions(self)
