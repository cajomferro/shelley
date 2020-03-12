from shelley.parser.events import parse as parse_events
from shelley.parser.actions import parse as parse_actions
from shelley.parser.behaviours import parse as parse_behaviours
from shelley.ast.devices import Device


class DButton(Device):
    name = 'Button'

    def __init__(self):
        i_events, e_events = parse_events('external begin, external pressed,external released')
        actions = parse_actions("")

        behaviours_str = "begin -> pressed,pressed -> released,released -> pressed"
        behaviours = parse_behaviours(behaviours_str, i_events.union(e_events), actions)

        super().__init__(self.name, actions, i_events, e_events, behaviours)


def create_device_button():
    return DButton()
