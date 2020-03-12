from shelley.parser.events import parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviours import parse as parse_behaviours
from shelley.ast.devices import Device


class DTimer(Device):
    name = 'Timer'

    def __init__(self):
        i_events, e_events = parse_events("external begin, internal started, internal canceled, external timeout")
        actions = parse_actions("start,cancel")

        behaviours_str = """begin -> start() started
            started -> cancel() canceled
            started -> timeout
            canceled -> start() started
            timeout -> start() started"""
        behaviours = parse_behaviours(behaviours_str, i_events.union(e_events), actions)

        super().__init__(self.name, actions, i_events, e_events, behaviours)


def create_device_timer():
    return DTimer()
