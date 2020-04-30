from shelley.ast.behaviors import Behaviors
from shelley.ast.events import Events
from shelley.ast.actions import Actions
from shelley.parser.events import parse as parse_events
from shelley.parser.actions import parse as parse_actions
import re


def parse(input: str, events: Events, actions: Actions) -> Behaviors:
    """

    """
    regex = r"(.*?)(?:\s->\s)(?:(.*?)(?:\(\))\s(.*?)|(.*?))(?:,|\n|$)"

    matches = re.finditer(regex, input, re.MULTILINE)

    behaviors = Behaviors()
    for match in matches:
        if match.group(4) is not None:
            e1 = events[match.group(1).strip()]
            e2 = events[match.group(4).strip()]
            behaviors.create(e1, e2)
        else:
            e1 = events[match.group(1).strip()]
            e2 = events[match.group(3).strip()]
            a = actions[match.group(2).strip()]
            behaviors.create(e1, e2, a)

    return behaviors


def test_parse():
    i_events, e_events = parse_events(
        "internal started, internal canceled, external timeout, external begin"
    )

    actions = parse_actions("start,cancel")

    input_str = """begin -> start() started
started -> cancel() canceled
started -> timeout
canceled -> start() started
timeout -> start() started"""

    behaviors = parse(input_str, i_events.merge(e_events), actions)
    print([(elem.e1.name, elem.e2.name, elem.action) for elem in behaviors._data])
