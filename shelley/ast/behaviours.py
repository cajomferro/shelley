from __future__ import annotations
from typing import List, Set, TYPE_CHECKING
import uuid
from dataclasses import dataclass

from .util import MyCollection
from .node import Node
from .events import GenericEvent, EEvent, IEvent
from .actions import Action

if TYPE_CHECKING:
    from ast.visitors import Visitor


@dataclass
class Behaviour(Node):
    uuid = uuid.uuid1()
    e1 = None  # type: GenericEvent
    e2 = None  # type: GenericEvent
    action = None  # type: Action

    def __init__(self, e1: GenericEvent, e2: GenericEvent, action: Action = None):
        self.e1 = e1
        self.e2 = e2
        self.action = action
        if isinstance(self.e2, IEvent) and self.action is None:
            raise BehaviourMissingActionForInternalEvent("Behaviour with internal event must specify an action")
        if isinstance(self.e2, EEvent) and self.action is not None:
            raise BehaviourUnexpectedActionForExternalEvent("Behaviour with external event does not require an action")

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_behaviour(self)

    def check(self, actions: Set[Action], events: Set[GenericEvent], behaviours: List[Behaviour]):
        self.check_action_is_declared(actions)
        self.check_event_is_declared(events)
        self.check_is_duplicated(behaviours)
        behaviours.append(self)

    def check_action_is_declared(self, actions: Set[Action]):
        if isinstance(self.e2, IEvent) and self.action not in actions:
            raise BehaviourActionForInternalEventUndeclared(
                "Action '{0}' not declared for internal event '{1}'".format(self.action.name,
                                                                            self.e2.name))

    def check_event_is_declared(self, events: Set[GenericEvent]):

        if self.e1 not in events:
            raise BehaviourEventUndeclared(
                "Left event '{0}' was not declared".format(self.e2.name))

        if self.e2 not in events:
            raise BehaviourEventUndeclared(
                "Right event '{0}' was not declared".format(self.e2.name))

    def check_is_duplicated(self, behaviours: List[Behaviour]):
        if self in behaviours:
            raise BehavioursListDuplicatedError(
                "Duplicated behaviour: {0} -> {1}".format(self.e1.name, self.e2.name))

    def __eq__(self, other):
        if not isinstance(other, Behaviour):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Behaviour type")

        return self.e1.name == other.e1.name and self.e2.name == other.e2.name

    def __hash__(self):
        return id(self.uuid)


class BehaviourMissingActionForInternalEvent(Exception):
    pass


class BehaviourUnexpectedActionForExternalEvent(Exception):
    pass


class BehavioursListEmptyError(Exception):
    pass


class BehaviourEventUndeclared(Exception):
    pass


class BehaviourActionForInternalEventUndeclared(Exception):
    pass


class BehavioursListDuplicatedError(Exception):
    pass


class BehavioursMissingBegin(Exception):
    pass


class Behaviours(Node, MyCollection[Behaviour]):

    def find_by_pair(self, e1: GenericEvent, e2: GenericEvent):
        re = None
        try:
            re = next(x for x in self._data if x.e1 == e1 and x.e2 == e2)
        except StopIteration:
            pass
        return re

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_actions(self)
