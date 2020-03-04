from typing import List
from actions import Action

# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re


# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.

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
