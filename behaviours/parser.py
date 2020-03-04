from typing import List
from behaviours import Behaviour
from events import EEvent, IEvent, GenericEvent
from events.parser import parse as parse_events
from actions.parser import parse as parse_actions
from actions import Action

# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re


def find_action(name: str, actions: List[Action]):
    result = [elem for elem in actions if elem.name == name]
    if len(result) == 0:
        raise Exception("Action {0} not found!".format(name))
    return result[0]


def find_event(name: str, events: List[GenericEvent]):
    result = [elem for elem in events if elem.name == name]
    if len(result) == 0:
        raise Exception("Event {0} not found!".format(name))
    return result[0]


def parse(input: str, events: List[GenericEvent], actions: List[Action]) -> List[Behaviour]:
    """
    :param events:
    :return:
    """
    regex = r"(.*?)(?:\s->\s)(?:(.*?)(?:\(\))\s(.*?)|(.*?))(?:,|\n|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    result = []  # type: List[Behaviour]
    for match in matches:
        if match.group(4) is not None:
            result.append(
                Behaviour(find_event(match.group(1).strip(), events), find_event(match.group(4).strip(), events)))
        else:
            result.append(
                Behaviour(find_event(match.group(1).strip(), events), find_event(match.group(3).strip(), events),
                          find_action(match.group(2).strip(),
                                      actions)))
    return result


if __name__ == "__main__":
    i_events = parse_events('internal started, internal canceled, external timeout, external begin')
    e_events = []

    actions = parse_actions("start,cancel")

    input_str = """begin -> start() started
started -> cancel() canceled
started -> timeout
canceled -> start() started
timeout -> start() started"""
    print([(elem.e1.name, elem.e2.name, elem.action) for elem in parse(input_str, i_events + e_events, actions)])
