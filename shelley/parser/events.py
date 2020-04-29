from typing import Tuple
from shelley.ast.events import EEvent, IEvent, IEvents, EEvents
import re

__all__ = (
    "EEvent",
    "IEvent",
    "IEvents",
    "EEvents",
    "parse_internal_events",
    "parse_external_events",
    "parse",
)


def parse_internal_events(input: str) -> IEvents:
    """
    :param events:
    :return:
    """
    regex = r"(internal\s(.+?))(?:,|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    events: IEvents = IEvents()
    for match in matches:
        events.add(IEvent(match.group(2).strip()))

    return events


def parse_external_events(input: str) -> EEvents:
    """
    :param events:
    :return:
    """
    regex = r"(external\s(.+?))(?:,|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    events: EEvents = EEvents()
    for match in matches:
        events.add(EEvent(match.group(2).strip()))

    return events


def parse(input: str) -> Tuple[IEvents, EEvents]:
    ievents = parse_internal_events(input)
    eevents = parse_external_events(input)
    return ievents, eevents


def test_parse() -> None:
    input_str = "internal started, internal canceled, external timeout"
    ievents, eevents = parse(input_str)
    print([elem.name for elem in ievents._data])
    print([elem.name for elem in eevents._data])
