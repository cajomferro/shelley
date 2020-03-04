from typing import List, Tuple

from actions import Action
from events import GenericEvent, IEvent, EEvent
from behaviours import Behaviour

BEGIN_EVENT = EEvent('begin')


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


def check(behaviours: List[Behaviour],
          actions: List[Action],
          i_events: List[IEvent],
          e_events: List[EEvent],
          result: List[Behaviour] = []) -> None:
    _check_behaviours(behaviours.copy(), actions.copy(), i_events.copy(), e_events.copy(), result)

    count = 0
    for behaviour in result:
        if behaviour.e1 == EEvent('begin'):
            count += 1
    if count == 0:
        raise BehavioursMissingBegin("'begin' must appear at least once")


def _check_behaviours(behaviours: List[Behaviour],
                      actions: List[Action],
                      i_events: List[IEvent],
                      e_events: List[EEvent],
                      result: List[Behaviour] = []):
    if len(behaviours) == 0:
        raise BehavioursListEmptyError("List of behaviours cannot be empty!")

    current_behaviour = behaviours.pop()  # pop from tail

    if len(behaviours) == 0:
        if current_behaviour.e1 not in i_events and current_behaviour.e1 not in e_events and current_behaviour.e1 != BEGIN_EVENT:
            raise BehaviourEventUndeclared("Left event must be declared either as internal or external event")

        if isinstance(current_behaviour.e2, EEvent) and current_behaviour.e2 not in e_events:
            raise BehaviourEventUndeclared(
                "Right external event '{0}' was not declared".format(current_behaviour.e2.name))

        if isinstance(current_behaviour.e2, IEvent):
            if current_behaviour.action not in actions:
                raise BehaviourActionForInternalEventUndeclared(
                    "Action '{0}' not declared for internal event '{1}'".format(current_behaviour.action.name,
                                                                                current_behaviour.e2.name))
            if current_behaviour.e2 not in i_events:
                raise BehaviourEventUndeclared(
                    "Right internal event '{0}' was not declared".format(current_behaviour.e2.name))

        if current_behaviour in result:
            raise BehavioursListDuplicatedError(
                "Duplicated behaviour: {0} -> {1}".format(current_behaviour.e1.name, current_behaviour.e2.name))

        result.append(current_behaviour)

    else:
        _check_behaviours([current_behaviour], actions, i_events, e_events, result)
        _check_behaviours(behaviours, actions, i_events, e_events, result)
