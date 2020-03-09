from typing import Set
from shelley.ast.actions import Action
import re


def parse(events: str) -> Set[Action]:
    """
    :param events:
    :return:
    """
    regex = r"(.+?)(?:,|$)"

    matches = re.finditer(regex, events, re.MULTILINE)

    result = set()  # type: Set[Action]
    for match in matches:
        result.add(Action(match.group(1).strip()))

    return result


def test_parse():
    input = "start, cancel"
    actions = parse(input)
    print([elem.name for elem in actions])
    assert len(actions) == 2


def test_duplicates():
    input = "start, start"
    actions = parse(input)
    print([elem.name for elem in actions])
    print(actions)
    assert len(actions) == 1
