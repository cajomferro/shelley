from __future__ import annotations
from typing import Set, TYPE_CHECKING

from .node import Node
from . import actions, find_instance_by_name

if TYPE_CHECKING:
    from ast.visitors import Visitor


class Action(Node):
    name = None  # type: str

    def __init__(self, name: str):
        self.name = name

    def __new__(cls, name: str):
        instance = find_instance_by_name(name, actions)
        if instance is None:
            instance = super(Action, cls).__new__(cls)
            actions.append(instance)
        return instance

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_action(self)

    def check(self, actions: Set[Action]):
        self.check_is_duplicated(actions)
        actions.append(self)

    def check_is_duplicated(self, actions: Set[Action]):
        if self in actions:
            raise ActionsListDuplicatedError("Duplicated action: {0}".format(self.name))

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
