# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

from .creator.correct import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from shelley.automata import Device as AutomataDevice
from shelley.ast.triggers import TriggerRule
from karakuri.regular import Regex

declared_devices = {}

d_led = create_device_led()
declared_devices[d_led.name] = d_led

d_button = create_device_button()
declared_devices[d_button.name] = d_button

d_timer = create_device_timer()
declared_devices[d_timer.name] = d_timer

d_desk_lamp = create_device_desk_lamp(d_led, d_button, d_timer)


# class Device:
#     events: List[str]
#     behavior: List[Tuple[str, str]]
#     components: Dict[str, str]
#     triggers: Dict[str, Regex]
#     known_devices: Dict[str, NFA]

# adevice = AutomataDevice()

def rules_to_regex(rule: TriggerRule) -> Regex:
    return ""


def test_button_structures():
    assert d_button.get_all_events().list_str() == ['begin', 'pressed', 'released']
    assert d_button.actions.list_str() == []
    assert d_button.behaviors.as_list_tuples() == [('begin', 'pressed'), ('pressed', 'released'),
                                                   ('released', 'pressed')]
    assert d_button.components.components_to_devices == {}
