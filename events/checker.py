from typing import List
from events import GenericEvent, IEvent, EEvent


class EventsListEmptyError(Exception):
    pass


class EventsListDuplicatedError(Exception):
    pass


def check(events: List[GenericEvent]) -> (List[IEvent], List[EEvent]):
    return _check_events(events.copy())


def _check_events(events: List[GenericEvent]) -> (List[IEvent], List[EEvent]):
    """
    Differing from the paper specification in that it returns lists (instead of sets)
    because it is easier to manipulate (e.g., compare) objects
    :param events:
    :return:
    """
    if len(events) == 0:
        raise EventsListEmptyError("List of events cannot be empty!")

    current_event = events.pop()  # pop from tail

    if len(events) == 0:
        if isinstance(current_event, IEvent):
            return [current_event], []
        elif isinstance(current_event, EEvent):
            return [], [current_event]

    else:
        s_internals, s_externals = check(events)

        if current_event in s_internals or current_event in s_externals:
            raise EventsListDuplicatedError("Duplicated event: {0}".format(current_event.name))

        if isinstance(current_event, IEvent):
            s_internals.append(current_event)

        elif isinstance(current_event, EEvent):
            s_externals.append(current_event)

        return s_internals, s_externals

# def check_events2(events: type(List[GenericEvent]),
#                   result_ievents: type(List[IEvent]),
#                   result_eevents: type(List[EEvent])):
#     """
#     Alternative not following exactly the specification
#     :param events:
#     :param result_ievents:
#     :param result_eevents:
#     :return:
#     """
#     if len(events) == 0:
#         raise EventsListEmptyError("List of events cannot be empty!")
#
#     current_event = events.pop()  # pop from tail
#
#     if current_event in result_ievents or current_event in result_eevents:
#         raise EventsListDuplicatedError("Duplicated event: {0}".format(current_event.name))
#
#     if isinstance(current_event, IEvent):
#         result_ievents.append(current_event)
#
#     elif isinstance(current_event, EEvent):
#         result_eevents.append(current_event)
#
#     #    if len(events) == 0:
#     #        return
#
#     if len(events) > 0:
#         check_events2(events, result_ievents, result_eevents)
