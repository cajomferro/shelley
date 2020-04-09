from .context import shelley

from karakuri.regular import NFA, nfa_to_regex, regex_to_nfa, Union, Char, Concat, concat, shuffle as And, \
    nfa_to_dfa, Star, NIL, VOID, DFA
from shelley.automata import *

B_P = "b.pressed"
B_R = "b.released"


def create_button():
    return NFA(
        # states=[0, 1],
        alphabet=[B_P, B_R],
        transition_func=NFA.transition_edges([
            (0, [B_P], 1),
            (1, [B_R], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


LA_ON = "ledA.on"
LA_OFF = "ledA.off"


def create_led_a():
    return NFA(
        # states=[0, 1],
        alphabet=[LA_ON, LA_OFF],
        transition_func=NFA.transition_edges([
            (0, [LA_ON], 1),
            (1, [LA_OFF], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


LB_ON = "ledB.on"
LB_OFF = "ledB.off"


def create_led_b():
    return NFA(
        # states=[0, 1],
        alphabet=[LB_ON, LB_OFF],
        transition_func=NFA.transition_edges([
            (0, [LB_ON], 1),
            (1, [LB_OFF], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


T_T = "t.timeout"
T_C = "t.canceled"
T_S = "t.started"


def create_timer():
    return NFA(
        # states=[0, 1],
        alphabet=[T_T, T_C, T_S],
        transition_func=NFA.transition_edges([
            (0, [T_S], 1),
            (1, [T_C, T_T], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


LEVEL1 = "level1"
LEVEL2 = "level2"
STANDBY1 = "standby1"
STANDBY2 = "standby2"


def create_hello_world():
    return NFA(
        alphabet=[LEVEL1, LEVEL2, STANDBY1, STANDBY2],
        transition_func=NFA.transition_edges([
            (0, [LEVEL1], 1),
            (1, [LEVEL2], 2),
            (1, [STANDBY1], 0),
            (2, [STANDBY2], 0),
        ]),
        start_state=0,
        accepted_states=lambda x: 0 <= x <= 2,
    )


def create_led_and_button():
    """
    This example should be a sub-behavior of shuffling button with led-a.
    
    (0) LEDA.ON --->  (1)  BTN.PRS ----> (2)
        <--- LEDA.OFF      <--- BTN.REL
    """
    return NFA(
        # states=[0, 1, 2],
        alphabet=[LA_ON, LA_OFF, B_R, B_P],
        transition_func=NFA.transition_edges([
            (0, [LA_ON], 1),
            (1, [LA_OFF], 0),
            (1, [B_P], 2),
            (2, [B_R], 1),
        ]),
        start_state=0,
        accepted_states=[0, 1, 2],
    )


def test_button():
    button = create_button()
    assert button.accepts([])
    assert button.accepts([B_P, B_R])
    assert button.accepts([B_P])
    assert not button.accepts([B_R])


def test_shuffle():
    button = create_button()
    led_a = create_led_a()
    both = button.shuffle(led_a)
    # Both should accept all behaviors of the button
    assert both.accepts([])
    assert both.accepts([B_P, B_R])
    assert both.accepts([B_P])
    assert not both.accepts([B_R])
    # It should also accept all behaviors of led
    assert both.accepts([LA_ON, LA_OFF])
    assert both.accepts([LA_ON])
    assert not both.accepts([LA_OFF])
    # Finally, it should accept interleaving of LED and Button:
    assert both.accepts([LA_ON, B_P, B_R, LA_OFF, B_P])
    # Here we fail because we have B_P followed by B_P
    assert not both.accepts([LA_ON, B_P, LA_OFF, B_P])


def test_led_and_button():
    both = create_led_and_button()
    # Both should accept all behaviors of the button
    assert both.accepts([])
    assert both.accepts([LA_ON])
    assert both.accepts([LA_ON, LA_OFF])
    # It should also accept all behaviors of led
    assert both.accepts([LA_ON, B_P])
    assert both.accepts([LA_ON, B_P, B_R, LA_OFF])
    assert both.accepts([LA_ON, B_P, B_R, LA_OFF, LA_ON])
    # Here we fail because we have B_P followed by B_P
    assert not both.accepts([B_R])
    assert not both.accepts([B_P])
    assert not both.accepts([LA_ON, B_R])
    assert not both.accepts([LA_ON, B_P, LA_OFF])


def test_contains():
    button = create_button()
    led_a = create_led_a()
    both = button.shuffle(led_a)
    behavior = create_led_and_button()
    assert nfa_to_dfa(both).contains(nfa_to_dfa(behavior))


def test_hello_world():
    HELLO_WORLD_TRIGGERS = {
        LEVEL1:
            Concat.from_list(map(Char, [B_P, B_R, LA_ON, T_S])),
        LEVEL2:
            Concat.from_list([
                Char(B_P),
                Char(B_R),
                And(Char(T_C), Char(LB_ON)),
                Char(T_S),
            ]),
        STANDBY1:
            concat(Char(T_T), Char(LA_OFF)),
        STANDBY2:
            concat(
                Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                And(Char(LB_OFF), Char(LA_OFF)),
            ),
    }
    components = [
        create_button(),
        create_led_a(),
        create_led_b(),
        create_timer()
    ]
    behavior = create_hello_world()
    assert get_invalid_behavior(components, nfa_to_regex(behavior), HELLO_WORLD_TRIGGERS) is None


def test_encode_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    be = encode_behavior(behavior, triggers, flatten=True, minimize=True)
    expected = nfa_to_dfa(regex_to_nfa(Star(Char(B_P)))).flatten(minimize=True)
    assert expected.contains(be)


def test_encode_behavior2_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    expected = encode_behavior(behavior, triggers, flatten=True, minimize=True)
    triggers2 = {
        LEVEL1: nfa_to_dfa(regex_to_nfa(Char(B_P))).minimize(),
        LEVEL2: nfa_to_dfa(regex_to_nfa(Char(B_R))).minimize(),
    }
    behavior_dfa = nfa_to_dfa(regex_to_nfa(behavior)).minimize()
    result = encode_behavior2(behavior_dfa, triggers2)
    assert isinstance(result, NFA)
    given = nfa_to_dfa(result).minimize()
    assert given.is_equivalent_to(expected)


def test_encode2():
    behavior = Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    triggers = {
        LEVEL1: Concat(Char(B_P), Char(B_P)),
        LEVEL2: NIL,
    }
    be = encode_behavior(behavior, triggers, flatten=True, minimize=True)
    expected = nfa_to_dfa(regex_to_nfa(Star(Concat(Char(B_P), Char(B_P))))).flatten(minimize=True)
    assert expected.contains(be)
    assert be.contains(expected)


def test_fail_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    assert get_invalid_behavior([create_button()], behavior, triggers) is not None


def test_ok_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    assert get_invalid_behavior([create_button()], behavior, triggers) is None


def test_fail_hello_world():
    hello = create_hello_world()
    assert hello.accepts([])
    behavior = nfa_to_regex(hello)
    triggers = {
        LEVEL1:
            Concat.from_list(map(Char, [B_P, B_R, LA_ON, T_S])),
        LEVEL2:
            Concat.from_list([
                Char(B_R),
                Char(B_P),
                And(Char(T_C), Char(LB_ON)),
                Char(T_S),
            ]),
        STANDBY1:
            concat(Char(T_T), Char(LA_OFF)),
        STANDBY2:
            concat(
                Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                And(Char(LB_OFF), Char(LA_OFF)),
            ),
    }
    components = [
        create_button(),
        create_led_a(),
        create_led_b(),
        create_timer()
    ]
    be = encode_behavior(behavior, triggers, flatten=True, minimize=True)
    assert be.accepts([])
    res = get_invalid_behavior(components, behavior, triggers)
    assert not res.accepts([])
    assert res is not None

def test_smallest_error():
    hello = create_hello_world()
    behavior = nfa_to_regex(hello)
    triggers = {
        LEVEL1:
            Concat.from_list(map(Char, [
                B_P,
                B_P, # <--- ERROR HERE: should be B_R
                LA_ON,
                T_S
            ])),
        LEVEL2:
            Concat.from_list([
                Char(B_P), #
                Char(B_R), # Omitted string
                And(Char(T_C), Char(LB_ON)),
                Char(T_S),
            ]),
        STANDBY1:
            concat(Char(T_T), Char(LA_OFF)),
        STANDBY2:
            concat(
                Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                And(Char(LB_OFF), Char(LA_OFF)),
            ),
    }
    components = [
        create_button(),
        create_led_a(),
        create_led_b(),
        create_timer()
    ]
    be = encode_behavior(behavior, triggers)
    res = get_invalid_behavior(components, behavior, triggers)
    err = res.get_shortest_string()
    assert res.accepts(err)
    assert err is not None
    assert err == (B_P, B_P, LA_ON, T_S)
    assert demultiplex(err) == {
        "b": ["pressed", "pressed"],
        "ledA": ["on"],
        "t": ["started"],
    }

def test_demultiplex():
    assert demultiplex(["a.a1", "b.b1", "c.c1", "b.b2", "a.a2"]) == {
        "a": ["a1", "a2"],
        "b": ["b1", "b2"],
        "c": ["c1"],
    }

def test_prefix_nfa():
    led = NFA(
        alphabet=["on", "off"],
        transition_func=NFA.transition_edges([
            (0, ["on"], 1),
            (1, ["off"], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )
    assert prefix_nfa(led, "ledA.") == create_led_a()


def test_build_components():
    led = NFA(
        alphabet=["on", "off"],
        transition_func=NFA.transition_edges([
            (0, ["on"], 1),
            (1, ["off"], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )
    comps = {
        "ledA": "LED",
        "ledB": "LED",
    }
    known_devs = {
        "LED": CheckedDevice(led),
    }
    given = dict(build_components(comps, known_devs))
    expected = {
        "ledA": create_led_a(),
        "ledB": create_led_b(),
    }
    assert expected == given
    assert len(expected) == len(given)
    for (ex, giv) in zip(expected, given):
        assert ex == giv


def test_build_behavior():
    start_events = ['level1']
    events = ['level1', 'standby1', 'level2', 'standby2']
    behavior = [
        ('level1', 'standby1'),
        ('level1', 'level2'),
        ('level2', 'standby2'),
        ('standby1', 'level1'),
        ('standby2', 'level1')
    ]
    tsx = [
        # Start events:
        ('start', 'level1', 'level1'),
        # (level1, standby1)
        ('level1', 'standby1', 'standby1'),
        ('level1', 'level2', 'level2'),
        ('level2', 'standby2', 'standby2'),
        ('standby1', 'level1', 'level1'),
        ('standby2', 'level1', 'level1'),
    ]
    accepted = set(x for x in events)
    accepted.add("start")
    expected = NFA(alphabet=set(events),
                   transition_func=NFA.transition_edges_split(tsx),
                   start_state="start",
                   accepted_states=accepted,
                   )
    assert build_behavior(behavior, start_events, events, "start") == expected
    # Make sure this is equivalent to HELLO WORLD
    assert nfa_to_dfa(build_behavior(behavior, start_events, events)).is_equivalent_to(nfa_to_dfa(create_hello_world()))


######################
#### TEST DEVICES ####
######################

def test_device_button():
    device = Device(
        start_events=['b.pressed'],
        events=['b.pressed', 'b.released'],
        behavior=[
            ('b.pressed', 'b.released'),
            ('b.released', 'b.pressed'),
        ],
        components={},
        triggers={
            'b.pressed': NIL,
            'b.released': NIL,
        },
    )
    expected = check_valid_device(device, {}).nfa.flatten()

    assert nfa_to_dfa(create_button()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_led_a():
    device = Device(
        start_events=['ledA.on'],
        events=['ledA.on', 'ledA.off'],
        behavior=[
            ('ledA.on', 'ledA.off'),
            ('ledA.off', 'ledA.on'),
        ],
        components={},
        triggers={
            'ledA.on': NIL,
            'ledA.off': NIL,
        },
    )
    expected = check_valid_device(device, {}).nfa.flatten()

    assert nfa_to_dfa(create_led_a()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_led_b():
    device = Device(
        start_events=['ledB.on'],
        events=['ledB.on', 'ledB.off'],
        behavior=[
            ('ledB.on', 'ledB.off'),
            ('ledB.off', 'ledB.on'),
        ],
        components={},
        triggers={
            'ledB.on': NIL,
            'ledB.off': NIL,
        },
    )
    expected = check_valid_device(device, {}).nfa.flatten()

    assert nfa_to_dfa(create_led_b()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_timer():
    device = Device(
        start_events=['t.started'],
        events=['t.started', 't.canceled', 't.timeout'],
        behavior=[
            ('t.started', 't.canceled'),
            ('t.started', 't.timeout'),
            ('t.canceled', 't.started'),
            ('t.timeout', 't.started')
        ],
        components={},
        triggers={
            't.started': NIL,
            't.canceled': NIL,
            't.timeout': NIL
        },
    )
    expected = check_valid_device(device, {}).nfa.flatten()

    assert nfa_to_dfa(create_timer()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_hello_world():
    device = Device(
        start_events=['level1'],
        events=['level1', 'level2', 'standby1', 'standby2'],
        behavior=[
            ('level1', 'standby1'),
            ('level1', 'level2'),
            ('level2', 'standby2'),
            ('standby1', 'level1'),
            ('standby2', 'level1')
        ],
        components={},
        triggers={
            'level1': NIL,
            'level2': NIL,
            'standby1': NIL,
            'standby2': NIL
        },
    )
    expected = check_valid_device(device, {}).nfa.flatten()

    assert nfa_to_dfa(create_hello_world()).is_equivalent_to(nfa_to_dfa(expected))

def get_basic_devices():
    return dict(
        Led=Device(
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
        ),
        Button=Device(
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
        ),
        Timer=Device(
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
    )

def get_basic_known_devices():
    return dict((k,check_valid_device(d, {})) for (k,d) in get_basic_devices().items())

def test_invalid_behavior_1():
    device = Device(
        start_events=['level1'],
        events=['level1', 'level2', 'standby1', 'standby2'],
        behavior=[
            ('level1', 'standby1'),
            ('level1', 'level2'),
            ('level2', 'standby2'),
            ('standby1', 'level1'),
            ('standby2', 'level1')
        ],
        components={
            "b": "Button",
            "ledA": "Led",
            "ledB": "Led",
            "t": "Timer",
        },
        triggers={
            LEVEL1:
                Concat.from_list(map(Char, [
                    B_P,
                    B_P, # <--- ERROR HERE: should be B_R
                    LA_ON,
                    T_S
                ])),
            LEVEL2:
                Concat.from_list([
                    Char(B_P),
                    Char(B_R),
                    And(Char(T_C), Char(LB_ON)),
                    Char(T_S),
                ]),
            STANDBY1:
                concat(Char(T_T), Char(LA_OFF)),
            STANDBY2:
                concat(
                    Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                    And(Char(LB_OFF), Char(LA_OFF)),
                ),
        },
    )
    given = check_valid_device(device, get_basic_known_devices())
    assert given.error_trace == (B_P, B_P, LA_ON, T_S)
    assert given.component_errors == {
        "b": (["pressed", "pressed"], 1),
    }

def test_invalid_behavior_2():
    device = Device(
        start_events=['level1'],
        events=['level1', 'level2', 'standby1', 'standby2'],
        behavior=[
            ('level1', 'standby1'),
            ('level1', 'level2'),
            ('level2', 'standby2'),
            ('standby1', 'level1'),
            ('standby2', 'level1')
        ],
        components={
            "b": "Button",
            "ledA": "Led",
            "ledB": "Led",
            "t": "Timer",
        },
        triggers={
            LEVEL1:
                Concat.from_list(map(Char, [
                    B_R, # <--- ERROR HERE: should be B_P
                    B_P, # <--- ERROR HERE: should be B_P
                    B_R, # <--- ERROR HERE: should be B_P
                    LA_ON,
                    T_S
                ])),
            LEVEL2:
                Concat.from_list([
                    Char(B_P),
                    Char(B_R),
                    And(Char(T_C), Char(LB_ON)),
                    Char(T_S),
                ]),
            STANDBY1:
                concat(Char(T_T), Char(LA_OFF)),
            STANDBY2:
                concat(
                    Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                    And(Char(LB_OFF), Char(LA_OFF)),
                ),
        },
    )
    given = check_valid_device(device, get_basic_known_devices())
    assert given.error_trace == (B_R, B_P, B_R, LA_ON, T_S)
    assert given.component_errors == {
        "b": (["released", "pressed", "released"], 0),
    }


def test_device_led_and_button():
    device = Device(
        start_events=['ledA.on'],
        events=['ledA.on', 'ledA.off', 'b.pressed', 'b.released'],
        behavior=[
            ('ledA.on', 'ledA.off'),
            ('ledA.on', 'b.pressed'),
            ('b.pressed', 'b.released'),
            ('b.released', 'ledA.off'),
            ('b.released', 'b.pressed'),
            ('ledA.off', 'ledA.on')
        ],
        components={},
        triggers={
            'ledA.on': NIL,
            'ledA.off': NIL,
            'b.pressed': NIL,
            'b.released': NIL
        },
    )
    expected = check_valid_device(device, {}).nfa.flatten()

    assert nfa_to_dfa(create_led_and_button()).is_equivalent_to(nfa_to_dfa(expected))
