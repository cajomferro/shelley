from typing import List
from events import GenericEvent, EEvent, IEvent

# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re


# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.

def parse_internal_events(input: str) -> List[IEvent]:
    """
    :param events:
    :return:
    """
    regex = r"(internal\s(.+?))(?:,|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    events = []  # type: List[IEvent]
    for match in matches:
        events.append(IEvent(match.group(2).strip()))

    return events


def parse_external_events(input: str) -> List[EEvent]:
    """
    :param events:
    :return:
    """
    regex = r"(external\s(.+?))(?:,|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    events = []  # type: List[EEvent]
    for match in matches:
        events.append(EEvent(match.group(2).strip()))

    return events


def parse(input: str) -> (List[GenericEvent], List[GenericEvent]):
    ievents = parse_internal_events(input)
    eevents = parse_external_events(input)
    return ievents, eevents


if __name__ == "__main__":
    input_str = "internal started, internal canceled, external timeout"
    ievents, eevents = parse(input_str)
    print([elem.name for elem in ievents])
    print([elem.name for elem in eevents])
