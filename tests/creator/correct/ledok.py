from shelley.parser.events import GenericEvent, parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviours import parse as parse_behaviours
from shelley.ast.devices import Device
from shelley.ast.rules import TriggerRuleFired

class DLed(Device):
    name = 'LED'

    def __init__(self):
        i_events, e_events = parse_events('internal on,internal off,external begin')

        actions = parse_actions("turnOn,turnOff")

        behaviours_str = "begin -> turnOn() on,on -> turnOff() off,off -> turnOn() on"
        behaviours = parse_behaviours(behaviours_str, i_events.union(e_events), actions)

        triggers = dict()
        triggers[GenericEvent("on")] = TriggerRuleFired()
        triggers[GenericEvent("off")] = TriggerRuleFired()

        super().__init__(self.name, actions, i_events, e_events, behaviours, triggers)


def create_device_led():
    return DLed()
