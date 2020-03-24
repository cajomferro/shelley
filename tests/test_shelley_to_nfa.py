# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

from typing import Dict

from .creator.correct import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from shelley.automata import Device, check_valid_device
from shelley.ast.triggers import Triggers
from shelley.ast.visitors.trules2regex import TRules2RegexVisitor
from karakuri.regular import Regex


def create_automata_button() -> Device:
    shelley_button = create_device_button()
    return Device(events=shelley_button.get_all_events().list_str(),
                  behavior=shelley_button.behaviors.as_list_tuples(),
                  components=shelley_button.components.components_to_devices,
                  triggers=get_regex_dict(shelley_button.triggers))


def create_automata_led() -> Device:
    shelley_led = create_device_led()
    return Device(events=shelley_led.get_all_events().list_str(),
                  behavior=shelley_led.behaviors.as_list_tuples(),
                  components=shelley_led.components.components_to_devices,
                  triggers=get_regex_dict(shelley_led.triggers))


def create_automata_timer() -> Device:
    shelley_timer = create_device_timer()
    return Device(events=shelley_timer.get_all_events().list_str(),
                  behavior=shelley_timer.behaviors.as_list_tuples(),
                  components=shelley_timer.components.components_to_devices,
                  triggers=get_regex_dict(shelley_timer.triggers))


def create_automata_desklamp() -> Device:
    shelley_desk_lamp = create_device_desk_lamp()
    return Device(events=shelley_desk_lamp.get_all_events().list_str(),
                  behavior=shelley_desk_lamp.behaviors.as_list_tuples(),
                  components=shelley_desk_lamp.components.components_to_devices,
                  triggers=get_regex_dict(shelley_desk_lamp.triggers))


def get_regex_dict(triggers: Triggers) -> Dict[str, Regex]:
    visitor = TRules2RegexVisitor()
    triggers.accept(visitor)
    return visitor.regex_dict


def test_button_automata():
    automata_button = create_automata_button()
    assert automata_button.events == ['begin', 'pressed', 'released']
    assert automata_button.behavior == [('begin', 'pressed'), ('pressed', 'released'),
                                        ('released', 'pressed')]
    assert automata_button.components == {}

    result_str = ""
    for key in automata_button.triggers:
        regex = automata_button.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string()))
    # print(result_str)
    assert result_str.strip() == """begin: []
pressed: []
released: []"""

    checked_button = check_valid_device(automata_button, {})
    assert checked_button is not None


def test_led_automata():
    automata_led = create_automata_led()
    assert automata_led.events == ['begin', 'on', 'off']
    assert automata_led.behavior == [('begin', 'on'), ('on', 'off'),
                                     ('off', 'on')]
    assert automata_led.components == {}

    result_str = ""
    for key in automata_led.triggers:
        regex = automata_led.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string()))
    # print(result_str)
    assert result_str.strip() == """begin: []
on: []
off: []"""

    checked_led = check_valid_device(automata_led, {})
    assert checked_led is not None


def test_timer_automata():
    automata_timer = create_automata_timer()
    assert automata_timer.events == ['begin', 'timeout', 'started', 'canceled']
    assert automata_timer.behavior == [('begin', 'started'), ('started', 'canceled'), ('started', 'timeout'),
                                       ('canceled', 'started'), ('timeout', 'started')]
    assert automata_timer.components == {}

    result_str = ""
    for key in automata_timer.triggers:
        regex = automata_timer.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string()))
    # print(result_str)
    assert result_str.strip() == """begin: []
started: []
canceled: []
timeout: []"""

    checked_timer = check_valid_device(automata_timer, {})
    assert checked_timer is not None


def test_desklamp_automata():
    automata_desklamp = create_automata_desklamp()
    assert automata_desklamp.events == ['begin', 'level1', 'level2', 'standby1', 'standby2']
    assert automata_desklamp.behavior == [('begin', 'level1'), ('level1', 'standby1'), ('level1', 'level2'),
                                          ('level2', 'standby2'), ('standby1', 'level1'), ('standby2', 'level1')]
    assert automata_desklamp.components == {'b': 'Button', 'ledA': 'Led', 'ledB': 'Led', 't': 'Timer'}

    result_str = ""
    for key in automata_desklamp.triggers:
        regex = automata_desklamp.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string()))

    expected_str = """begin: b.begin \\cdot ledA.begin \\cdot ledB.begin \\cdot t.begin
level1: b.pressed \cdot b.released \cdot ledA.on \cdot t.started
level2: b.pressed \cdot (b.released \cdot ((t.canceled \cdot ledB.on + ledB.on \cdot t.canceled) \cdot t.started))
standby1: t.timeout \cdot ledA.off
standby2: (b.pressed \cdot b.released \cdot t.canceled + t.timeout) \cdot (ledB.off \cdot ledA.off + ledA.off \cdot ledB.off)"""
    print(result_str)
    assert result_str.strip() == expected_str

    known_devices = {'Led': check_valid_device(create_automata_led(), {}),
                     'Button': check_valid_device(create_automata_button(), {}),
                     'Timer': check_valid_device(create_automata_timer(), {})}

    checked_desklamp = check_valid_device(automata_desklamp, known_devices)
    assert checked_desklamp is not None
