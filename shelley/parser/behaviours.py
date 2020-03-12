from typing import Set
from shelley.ast.behaviours import Behaviour
from shelley.ast.events import GenericEvent
from shelley.ast.actions import Action
from .events import parse as parse_events
from .actions import parse as parse_actions
import re


def find_action(name: str, actions: Set[Action]):
    result = [elem for elem in actions if elem.name == name]
    if len(result) == 0:
        raise Exception("Action {0} not found!".format(name))
    return result[0]


def find_event(name: str, events: Set[GenericEvent]):
    result = [elem for elem in events if elem.name == name]
    if len(result) == 0:
        raise Exception("Event {0} not found!".format(name))
    return result[0]


def parse(input: str, events: Set[GenericEvent], actions: Set[Action]) -> Set[Behaviour]:
    """

    """
    regex = r"(.*?)(?:\s->\s)(?:(.*?)(?:\(\))\s(.*?)|(.*?))(?:,|\n|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    result = set()  # type: Set[Behaviour]
    for match in matches:
        if match.group(4) is not None:
            result.add(
                Behaviour(find_event(match.group(1).strip(), events), find_event(match.group(4).strip(), events)))
        else:
            result.add(
                Behaviour(find_event(match.group(1).strip(), events), find_event(match.group(3).strip(), events),
                          find_action(match.group(2).strip(),
                                      actions)))
    return result


def test_parse():
    i_events, e_events = parse_events('internal started, internal canceled, external timeout, external begin')

    actions = parse_actions("start,cancel")

    input_str = """begin -> start() started
started -> cancel() canceled
started -> timeout
canceled -> start() started
timeout -> start() started"""
    print([(elem.e1.name, elem.e2.name, elem.action) for elem in parse(input_str, i_events.union(e_events), actions)])
