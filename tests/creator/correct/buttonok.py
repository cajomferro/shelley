from shelley.parser.events import GenericEvent, EEvent, parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviors import parse as parse_behaviours
from shelley.ast.devices import Device
from shelley.ast.rules import TriggerRuleFired
from shelley.ast.triggers import Triggers


class DButton(Device):
    name = 'Button'

    def __init__(self):
        i_events, e_events = parse_events('external begin, external pressed,external released')
        actions = parse_actions("")
        start_events = ['begin']
        behaviours_str = "begin -> pressed,pressed -> released,released -> pressed"
        behaviors = parse_behaviours(behaviours_str, i_events.merge(e_events), actions)

        triggers = Triggers()
        triggers.create(e_events.find_by_name("begin"), TriggerRuleFired())
        triggers.create(e_events.find_by_name("pressed"), TriggerRuleFired())
        triggers.create(e_events.find_by_name("released"), TriggerRuleFired())

        super().__init__(self.name, actions, i_events, e_events, start_events, behaviors, triggers)


def create_device_button():
    return DButton()
