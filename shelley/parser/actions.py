from shelley.ast.actions import Actions
import re


def parse(events: str) -> Actions:
    """
    :param events:
    :return:
    """
    regex = r"(.+?)(?:,|$)"

    matches = re.finditer(regex, events, re.MULTILINE)

    result = Actions()  # type: Actions
    for match in matches:
        action_name = match.group(1).strip()
        result.create(action_name)

    return result


def test_parse():
    input = "start, cancel"
    actions = parse(input)
    print([elem.name for elem in actions._data])
    assert actions.count() == 2
