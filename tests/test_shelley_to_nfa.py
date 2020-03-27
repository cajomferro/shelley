# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

from typing import Dict

import yaml
from karakuri.regular import Regex, nfa_to_regex, dfa_to_nfa, Char, Concat, Union, Nil

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
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


def get_automata_device(name: str) -> AutomataDevice:
    shelley_device = get_shelley_device(name)
    return AutomataDevice(start_event='begin',
                          events=shelley_device.get_all_events().list_str(),
                          behavior=shelley_device.behaviors.as_list_tuples(),
                          components=shelley_device.components.components_to_devices,
                          triggers=get_regex_dict(shelley_device.triggers))


def test_button():
    expected = AutomataDevice(
        start_event='begin',
        events=['begin', 'pressed', 'released'],
        behavior=[
            ('begin', 'pressed'),
            ('pressed', 'released'),
            ('released', 'pressed'),
        ],
        components={},
        triggers={
            'pressed': Nil,
            'released': Nil,
        },
    )
    assert expected == get_automata_device('button')


def test_led():
    expected = AutomataDevice(
        start_event='begin',
        events=['begin', 'on', 'off'],
        behavior=[
            ('begin', 'on'),
            ('on', 'off'),
            ('off', 'on'),
        ],
        components={},
        triggers={
            'on': Nil,
            'off': Nil,
        },
    )
    assert expected == get_automata_device('led')

    #    checked_led = check_valid_device(automata, {})
    #    assert isinstance(checked_led, CheckedDevice)


def test_timer():
    expected = AutomataDevice(
        start_event='begin',
        events=['begin', 'started', 'canceled', 'timeout'],
        behavior=[
            ('begin', 'started'),
            ('started', 'canceled'),
            ('started', 'timeout'),
            ('canceled', 'started'),
            ('timeout', 'started')
        ],
        components={},
        triggers={
            'started': Nil,
            'canceled': Nil,
            'timeout': Nil
        },
    )
    assert expected == get_automata_device('timer')


def test_smartbutton1():
    expected = AutomataDevice(
        start_event='begin',
        events=['begin', 'on'],
        behavior=[
            ('begin', 'on'),
            ('on', 'on')
        ],
        components={'b': 'Button'},
        triggers={
            'on': Concat(Char('b.pressed'), Char('b.released'))
        },
    )
    assert expected == get_automata_device('smartbutton1')

    # known_devices = {'Button': check_valid_device(get_automata_device('button'), {})}
    #
    # checked_automata = check_valid_device(automata, known_devices)
    # print()
    # print(checked_automata.dfa)
    # # print(dfa_to_nfa(checked_automata.dfa))
    # print(nfa_to_regex(dfa_to_nfa(checked_automata.dfa)).to_string(app_str=lambda x, y: x + " ; " + y))

    # assert isinstance(checked_automata, CheckedDevice)


def test_desklamp():
    automata = get_automata_device('desklamp')

    assert automata.events == ['begin', 'level1', 'standby1', 'level2', 'standby2']
    assert automata.behavior == [('begin', 'level1'), ('level1', 'standby1'), ('level1', 'level2'),
                                 ('level2', 'standby2'), ('standby1', 'level1'), ('standby2', 'level1')]
    assert automata.components == {'b': 'Button', 'ledA': 'Led', 'ledB': 'Led', 't': 'Timer'}

    result_str = ""
    for key in automata.triggers:
        regex = automata.triggers[key]
        result_str += ("{0}: {1}\n".format(key, regex.to_string(app_str=lambda x, y: x + " ; " + y)))

    # begin: b.begin ; ledA.begin ; ledB.begin ; t.begin
    expected_str = """level1: b.pressed ; b.released ; ledA.on ; t.started
level2: b.pressed ; b.released ; ((t.canceled ; ledB.on + ledB.on ; t.canceled) ; t.started)
standby1: t.timeout ; ledA.off
standby2: (b.pressed ; b.released ; t.canceled + t.timeout) ; (ledB.off ; ledA.off + ledA.off ; ledB.off)"""

    assert result_str.strip() == expected_str

    known_devices = {'Led': check_valid_device(get_automata_device('led'), {}),
                     'Button': check_valid_device(get_automata_device('button'), {}),
                     'Timer': check_valid_device(get_automata_device('timer'), {})}

    checked_desklamp = check_valid_device(automata, known_devices)
    print(nfa_to_regex(dfa_to_nfa(checked_desklamp.dfa)).to_string(app_str=lambda x, y: x + " ; " + y))

    # assert isinstance(checked_desklamp, CheckedDevice)
