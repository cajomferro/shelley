# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

from typing import Dict

import yaml

from karakuri.regular import Regex, nfa_to_regex, dfa_to_nfa

from shelley.karakuri import Device as KarakuriDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.ast.triggers import Triggers
from shelley.ast.visitors.trules2regex import TRules2RegexVisitor
from shelley.yaml_parser import create_device_from_yaml


def get_shelley_device(name: str) -> ShelleyDevice:
    with open('tests/input/{0}.yaml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    return create_device_from_yaml(yaml_code)


def get_regex_dict(triggers: Triggers) -> Dict[str, Regex]:
    visitor = TRules2RegexVisitor()
    triggers.accept(visitor)
    return visitor.regex_dict


def get_karakuri_device(name: str) -> KarakuriDevice:
    shelley_device = get_shelley_device(name)
    return KarakuriDevice(events=shelley_device.get_all_events().list_str(),
                          behavior=shelley_device.behaviors.as_list_tuples(),
                          components=shelley_device.components.components_to_devices,
                          triggers=get_regex_dict(shelley_device.triggers))


def test_button_karakuri():
    karakuri = get_karakuri_device('button')

    assert karakuri.events == ['begin', 'pressed', 'released']
    assert karakuri.behavior == [('begin', 'pressed'), ('pressed', 'released'),
                                 ('released', 'pressed')]
    assert karakuri.components == {}

    result_str = ""
    for key in karakuri.triggers:
        regex = karakuri.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string()))

    assert result_str.strip() == """begin: []
pressed: []
released: []"""

    checked_button = check_valid_device(karakuri, {})
    assert isinstance(checked_button, CheckedDevice)


def test_led_karakuri():
    karakuri = get_karakuri_device('led')

    assert karakuri.events == ['begin', 'on', 'off']
    assert karakuri.behavior == [('begin', 'on'), ('on', 'off'),
                                 ('off', 'on')]
    assert karakuri.components == {}

    result_str = ""
    for key in karakuri.triggers:
        regex = karakuri.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string()))

    assert result_str.strip() == """begin: []
on: []
off: []"""

    checked_led = check_valid_device(karakuri, {})
    assert isinstance(checked_led, CheckedDevice)


def test_timer_karakuri():
    karakuri = get_karakuri_device('timer')

    assert karakuri.events == ['begin', 'started', 'canceled', 'timeout']
    assert karakuri.behavior == [('begin', 'started'), ('started', 'canceled'), ('started', 'timeout'),
                                 ('canceled', 'started'), ('timeout', 'started')]
    assert karakuri.components == {}

    result_str = ""
    for key in karakuri.triggers:
        regex = karakuri.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string()))

    assert result_str.strip() == """begin: []
started: []
canceled: []
timeout: []"""

    checked_timer = check_valid_device(karakuri, {})
    assert isinstance(checked_timer, CheckedDevice)


def test_desklamp_karakuri():
    karakuri = get_karakuri_device('desklamp')

    assert karakuri.events == ['begin', 'level1', 'standby1', 'level2', 'standby2']
    assert karakuri.behavior == [('begin', 'level1'), ('level1', 'standby1'), ('level1', 'level2'),
                                 ('level2', 'standby2'), ('standby1', 'level1'), ('standby2', 'level1')]
    assert karakuri.components == {'b': 'Button', 'ledA': 'Led', 'ledB': 'Led', 't': 'Timer'}

    result_str = ""
    for key in karakuri.triggers:
        regex = karakuri.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string(app_str=lambda x, y: x + " ; " + y)))

    # begin: b.begin ; ledA.begin ; ledB.begin ; t.begin
    expected_str = """level1: b.pressed ; b.released ; ledA.on ; t.started
level2: b.pressed ; b.released ; ((t.canceled ; ledB.on + ledB.on ; t.canceled) ; t.started)
standby1: t.timeout ; ledA.off
standby2: (b.pressed ; b.released ; t.canceled + t.timeout) ; (ledB.off ; ledA.off + ledA.off ; ledB.off)"""

    assert result_str.strip() == expected_str

    known_devices = {'Led': check_valid_device(get_karakuri_device('led'), {}),
                     'Button': check_valid_device(get_karakuri_device('button'), {}),
                     'Timer': check_valid_device(get_karakuri_device('timer'), {})}

    checked_desklamp = check_valid_device(karakuri, known_devices)
    print(nfa_to_regex(dfa_to_nfa(checked_desklamp.dfa)).to_string(app_str=lambda x, y: x + " ; " + y))

    #assert isinstance(checked_desklamp, CheckedDevice)
