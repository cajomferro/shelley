from typing import Set
from shelley.ast.events import GenericEvent, EEvent, IEvent
import re


def parse_internal_events(input: str) -> Set[IEvent]:
    """
    :param events:
    :return:
    """
    regex = r"(internal\s(.+?))(?:,|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    events = set()  # type: Set[IEvent]
    for match in matches:
        events.add(IEvent(match.group(2).strip()))

    return events


def parse_external_events(input: str) -> Set[EEvent]:
    """
    :param events:
    :return:
    """
    regex = r"(external\s(.+?))(?:,|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    events = set()  # type: Set[EEvent]
    for match in matches:
        events.add(EEvent(match.group(2).strip()))

    return events


def parse(input: str) -> (Set[GenericEvent], Set[GenericEvent]):
    ievents = parse_internal_events(input)
    eevents = parse_external_events(input)
    return ievents, eevents


def test_parse():
    input_str = "internal started, internal canceled, external timeout"
    ievents, eevents = parse(input_str)
    print([elem.name for elem in ievents])
    print([elem.name for elem in eevents])
