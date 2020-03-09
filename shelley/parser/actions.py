from typing import List
from shelley.ast.actions import Action
import re


def parse(events: str) -> List[Action]:
    """
    :param events:
    :return:
    """
    regex = r"(.+?)(?:,|$)"

    matches = re.finditer(regex, events, re.MULTILINE)

    result = []  # type: List[Action]
    for match in matches:
        result.append(Action(match.group(1).strip()))

    return result


if __name__ == "__main__":
    input = "start, cancel"
    print([elem.name for elem in parse(input)])
