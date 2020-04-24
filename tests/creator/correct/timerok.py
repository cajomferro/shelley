from shelley.parser.events import IEvent, EEvent, parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviors import parse as parse_behaviours
from shelley.ast.devices import Device
from shelley.ast.rules import TriggerRuleFired
from shelley.ast.triggers import Triggers


class DTimer(Device):
    name = 'Timer'

    def __init__(self):
        i_events, e_events = parse_events("external begin, internal started, internal canceled, external timeout")
        actions = parse_actions("start,cancel")
        start_events = ['begin']

        behaviours_str = """begin -> start() started
            started -> cancel() canceled
            started -> timeout
            canceled -> start() started
            timeout -> start() started"""
        behaviours = parse_behaviours(behaviours_str, i_events.merge(e_events), actions)

        triggers = Triggers()
        triggers.create(e_events.find_by_name("begin"), TriggerRuleFired())
        triggers.create(i_events.find_by_name("started"), TriggerRuleFired())
        triggers.create(i_events.find_by_name("canceled"), TriggerRuleFired())
        triggers.create(e_events.find_by_name("timeout"), TriggerRuleFired())

        super().__init__(self.name, actions, i_events, e_events, start_events, behaviours, triggers)


def create_device_timer() -> DTimer:
    return DTimer()
