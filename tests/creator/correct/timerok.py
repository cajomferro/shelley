from shelley.parser.events import GenericEvent, parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviours import parse as parse_behaviours
from shelley.ast.devices import Device
from shelley.ast.rules import TriggerRuleFired


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

        triggers = dict()
        triggers[GenericEvent("started")] = TriggerRuleFired()
        triggers[GenericEvent("canceled")] = TriggerRuleFired()
        triggers[GenericEvent("timeout")] = TriggerRuleFired()

        super().__init__(self.name, actions, i_events, e_events, behaviours, triggers)


def create_device_timer():
    return DTimer()
