from __future__ import annotations
from typing import List, TYPE_CHECKING

from ast.node import Node
from ast.events import GenericEvent, EEvent, IEvent
from ast.actions import Action


if TYPE_CHECKING:
    from ast.visitors import Visitor



class Behaviour(Node):
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

    def check(self, actions: List[Action], events: List[GenericEvent], behaviours: List[Behaviour]):
        self.check_action_is_declared(actions)
        self.check_event_is_declared(events)
        self.check_is_duplicated(behaviours)
        behaviours.append(self)

    def check_action_is_declared(self, actions: List[Action]):
        if isinstance(self.e2, IEvent) and self.action not in actions:
            raise BehaviourActionForInternalEventUndeclared(
                "Action '{0}' not declared for internal event '{1}'".format(self.action.name,
                                                                            self.e2.name))

    def check_event_is_declared(self, events: List[GenericEvent]):

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
