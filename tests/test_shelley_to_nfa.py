# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

from typing import Dict

from .creator.correct import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from shelley.automata import Device as AutomataDevice
from shelley.ast.triggers import Trigger, Triggers
from shelley.ast.rules import TriggerRule
from shelley.ast.visitors.trules2regex import TRules2RegexVisitor
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

def get_regex_dict(triggers: Triggers) -> Dict[str, Regex]:
    visitor = TRules2RegexVisitor()
    triggers.accept(visitor)
    return visitor.regex_dict


def test_button_structures():
    assert d_button.get_all_events().list_str() == ['begin', 'pressed', 'released']
    assert d_button.actions.list_str() == []
    assert d_button.behaviors.as_list_tuples() == [('begin', 'pressed'), ('pressed', 'released'),
                                                   ('released', 'pressed')]
    assert d_button.components.components_to_devices == {}
    assert get_regex_dict(d_button.triggers) == {}


def test_desklamp_triggers():
    regex_dict = get_regex_dict(d_desk_lamp.triggers)
    result_str = ""
    for key in regex_dict:
        if key != 'begin':
            regex = regex_dict[key]
            result_str += ("{0}: {1}\n".format(key, regex.to_string()))

    expected_str = """level1: b.pressed \cdot b.released \cdot ledA.on \cdot t.started
level2: (b.pressed \cdot b.released \cdot (t.canceled \cdot ledB.on + ledB.on \cdot t.canceled)) \cdot t.started
standby1: t.timeout \cdot ledA.off
standby2: (b.pressed \cdot b.released \cdot t.canceled + t.timeout) \cdot (ledB.off \cdot ledA.off + ledA.off \cdot ledB.off)"""
    print(result_str)
    assert result_str.strip() == expected_str
