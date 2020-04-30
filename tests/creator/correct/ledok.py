from shelley.parser.events import EEvent, parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviors import parse as parse_behaviours
from shelley.ast.devices import Device
from shelley.ast.rules import TriggerRuleFired
from shelley.ast.triggers import Triggers


class DLed(Device):
    name = "Led"

    def __init__(self) -> None:
        i_events, e_events = parse_events("internal on,internal off,external begin")

        actions = parse_actions("turnOn,turnOff")

        start_events = ["begin"]

        behaviours_str = "begin -> turnOn() on,on -> turnOff() off,off -> turnOn() on"
        behaviours = parse_behaviours(behaviours_str, i_events.merge(e_events), actions)

        triggers = Triggers()
        names = ["begin", "on", "off"]
        for name in names:
            ev = e_events.find_by_name(name)
            assert ev is not None
            triggers.create(ev, TriggerRuleFired())

        super().__init__(
            self.name, actions, i_events, e_events, start_events, behaviours, triggers
        )


def create_device_led() -> DLed:
    return DLed()
