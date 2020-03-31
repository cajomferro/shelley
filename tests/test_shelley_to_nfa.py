# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

import yaml
from karakuri.regular import Char, Concat, Union, NIL

from shelley.automata import Device as AutomataDevice
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    with open('examples/{0}.yaml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley2automata(shelley)


def test_button():
    expected = AutomataDevice(
        start_events=['pressed'],
        events=['pressed', 'released'],
        behavior=[
            ('pressed', 'released'),
            ('released', 'pressed'),
        ],
        components={},
        triggers={
            'pressed': NIL,
            'released': NIL,
        },
    )
    assert expected == _get_automata_from_yaml('button')


def test_led():
    expected = AutomataDevice(
        start_events=['on'],
        events=['on', 'off'],
        behavior=[
            ('on', 'off'),
            ('off', 'on'),
        ],
        components={},
        triggers={
            'on': NIL,
            'off': NIL,
        },
    )
    assert expected == _get_automata_from_yaml('led')


def test_timer():
    expected = AutomataDevice(
        start_events=['started'],
        events=['started', 'canceled', 'timeout'],
        behavior=[
            ('started', 'canceled'),
            ('started', 'timeout'),
            ('canceled', 'started'),
            ('timeout', 'started')
        ],
        components={},
        triggers={
            'started': NIL,
            'canceled': NIL,
            'timeout': NIL
        },
    )
    assert expected == _get_automata_from_yaml('timer')


def test_smartbutton1():
    expected = AutomataDevice(
        start_events=['on'],
        events=['on'],
        behavior=[
            ('on', 'on')
        ],
        components={'b': 'Button'},
        triggers={
            'on': Concat(Char('b.pressed'), Char('b.released'))
        },
    )
    assert expected == _get_automata_from_yaml('smartbutton1')


def test_desklamp():
    expected_str = """standby2: (b.pressed ; b.released ; t.canceled + t.timeout) ; (ledB.off ; ledA.off + ledA.off ; ledB.off)"""

    expected = AutomataDevice(
        start_events=['level1'],
        events=['level1', 'standby1', 'level2', 'standby2'],
        behavior=[
            ('level1', 'standby1'), ('level1', 'level2'),
            ('level2', 'standby2'), ('standby1', 'level1'), ('standby2', 'level1')
        ],
        components={'b': 'Button', 'ledA': 'Led', 'ledB': 'Led', 't': 'Timer'},
        triggers={
            'level1': Concat(
                Char('b.pressed'),
                Concat(
                    Char('b.released'),
                    Concat(
                        Char('ledA.on'),
                        Char('t.started')))),
            'level2': Concat(
                Char('b.pressed'),
                Concat(
                    Char('b.released'),
                    Concat(
                        Union(
                            Concat(Char('t.canceled'), Char('ledB.on')),
                            Concat(Char('ledB.on'), Char('t.canceled'))
                        ),
                        Char('t.started')))),
            'standby1': Concat(Char('t.timeout'), Char('ledA.off')),
            'standby2': Concat(
                Union(
                    Concat(
                        Char('b.pressed'),
                        Concat(
                            Char('b.released'),
                            Char('t.canceled')
                        )
                    ),
                    Char('t.timeout')
                ),
                Union(
                    Concat(
                        Char('ledB.off'),
                        Char('ledA.off')
                    ),
                    Concat(
                        Char('ledA.off'),
                        Char('ledB.off')
                    )
                ))
        },
    )
    assert expected == _get_automata_from_yaml('desklamp')
