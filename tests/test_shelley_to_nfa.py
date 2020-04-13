# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

from pathlib import Path
from karakuri.regular import Char, Concat, Union, NIL

from shelley.automata import Device as AutomataDevice
from shelley.shelley2automata import shelley2automata
from shelley import yaml2shelley


def _get_path(device_name: str) -> Path:
    return Path('tests/input/') / '{0}.yml'.format(device_name)


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
    assert expected == shelley2automata(yaml2shelley.get_shelley_from_yaml(_get_path('button')))


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
    assert expected == shelley2automata(yaml2shelley.get_shelley_from_yaml(_get_path('led')))


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
    assert expected == shelley2automata(yaml2shelley.get_shelley_from_yaml(_get_path('timer')))


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
    assert expected == shelley2automata(yaml2shelley.get_shelley_from_yaml(_get_path('smartbutton1')))


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
    assert expected == shelley2automata(yaml2shelley.get_shelley_from_yaml(_get_path('desklamp')))
