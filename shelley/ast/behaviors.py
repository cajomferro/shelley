from __future__ import annotations
from typing import List, Set, TYPE_CHECKING
from dataclasses import dataclass

from .util import MyCollection
from .node import Node
from .events import GenericEvent, EEvent, IEvent
from .actions import Action

if TYPE_CHECKING:
    from ast.visitors import Visitor


@dataclass(order=True)
class Behavior(Node):
    e1: GenericEvent
    e2: GenericEvent
    action: Action

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_behaviour(self)

    def check(self, actions: Set[Action], events: Set[GenericEvent], behaviours: List[Behavior]):
        self.check_action_is_declared(actions)
        self.check_event_is_declared(events)
        self.check_is_duplicated(behaviours)
        behaviours.append(self)

    def check_action_is_declared(self, actions: Set[Action]):
        if isinstance(self.e2, IEvent) and self.action not in actions:
            raise BehaviorActionForInternalEventUndeclared(
                "Action '{0}' not declared for internal event '{1}'".format(self.action.name,
                                                                            self.e2.name))

    def check_event_is_declared(self, events: Set[GenericEvent]):

        if self.e1 not in events:
            raise BehaviorEventUndeclared(
                "Left event '{0}' was not declared".format(self.e2.name))

        if self.e2 not in events:
            raise BehaviorEventUndeclared(
                "Right event '{0}' was not declared".format(self.e2.name))

    def check_is_duplicated(self, behaviours: List[Behavior]):
        if self in behaviours:
            raise BehaviorsListDuplicatedError(
                "Duplicated behaviour: {0} -> {1}".format(self.e1.name, self.e2.name))

    # def __init__(self, e1: GenericEvent, e2: GenericEvent, action: Action = None):
    #     self.e1 = e1
    #     self.e2 = e2
    #     self.action = action
    #     if isinstance(self.e2, IEvent) and self.action is None:
    #         raise BehaviourMissingActionForInternalEvent("Behaviour with internal event must specify an action")
    #     if isinstance(self.e2, EEvent) and self.action is not None:
    #         raise BehaviourUnexpectedActionForExternalEvent("Behaviour with external event does not require an action")
    #
    # def __eq__(self, other):
    #     if not isinstance(other, Behaviour):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance is not of Behaviour type")
    #
    #     return self.e1.name == other.e1.name and self.e2.name == other.e2.name
    #
    # def __hash__(self):
    #     return id(self.uuid)


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


class Behaviors(Node, MyCollection[Behavior]):
    _data = None  # type: List[Behavior]

    def __init__(self):
        self._data = list()

    def create(self, e1: GenericEvent, e2: GenericEvent, a: Action = None) -> Behavior:
        behavior = Behavior(e1, e2, a)
        if behavior not in self._data:
            self._data.append(behavior)
        else:
            raise BehaviorsListDuplicatedError()
        return behavior

    def contains_events_pair(self, e1_name: str, e2_name: str) -> bool:
        return False if self.find_by_event_pair(e1_name, e2_name) is None else True

    def find_by_event_pair(self, e1_name: str, e2_name: str) -> Behavior:
        re = None
        try:
            re = next(x for x in self._data if x.e1.name == e1_name and x.e2.name == e2_name)
        except StopIteration:
            pass
        return re

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_behaviors(self)
