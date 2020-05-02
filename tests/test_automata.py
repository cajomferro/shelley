import pytest
from typing import Dict, cast, List
from karakuri.regular import (
    NFA,
    regex_to_nfa,
    Union,
    Char,
    Concat,
    concat,
    shuffle as And,
    nfa_to_dfa,
    Star,
    NIL,
    Regex,
)
from shelley.automata import Device, AssembledDevice, CheckedDevice
from shelley import automata

B_P: str = "b.pressed"
B_R: str = "b.released"


def create_prefixed_button() -> NFA:
    return NFA(
        # states=[0, 1],
        alphabet=[B_P, B_R],
        transition_func=NFA[int, str].transition_edges(
            [(0, set([B_P]), 1), (1, set([B_R]), 0),]
        ),
        start_state=0,
        accepted_states=[0, 1],
    )


LA_ON = "ledA.on"
LA_OFF = "ledA.off"


def create_prefixed_led_a() -> NFA:
    return NFA(
        # states=[0, 1],
        alphabet=[LA_ON, LA_OFF],
        transition_func=NFA.transition_edges([(0, [LA_ON], 1), (1, [LA_OFF], 0),]),
        start_state=0,
        accepted_states=[0, 1],
    )


LB_ON = "ledB.on"
LB_OFF = "ledB.off"


def create_prefixed_led_b() -> NFA:
    return NFA(
        # states=[0, 1],
        alphabet=[LB_ON, LB_OFF],
        transition_func=NFA.transition_edges([(0, [LB_ON], 1), (1, [LB_OFF], 0),]),
        start_state=0,
        accepted_states=[0, 1],
    )


T_T = "t.timeout"
T_C = "t.canceled"
T_S = "t.started"


def create_prefixed_timer() -> NFA:
    return NFA(
        # states=[0, 1],
        alphabet=[T_T, T_C, T_S],
        transition_func=NFA.transition_edges([(0, [T_S], 1), (1, [T_C, T_T], 0),]),
        start_state=0,
        accepted_states=[0, 1],
    )


LEVEL1 = "level1"
LEVEL2 = "level2"
STANDBY1 = "standby1"
STANDBY2 = "standby2"


def create_hello_world() -> NFA:
    def is_final(x: int) -> bool:
        return 0 <= x <= 2

    return NFA(
        alphabet=[LEVEL1, LEVEL2, STANDBY1, STANDBY2],
        transition_func=NFA.transition_edges(
            [
                (0, [LEVEL1], 1),
                (1, [LEVEL2], 2),
                (1, [STANDBY1], 0),
                (2, [STANDBY2], 0),
            ]
        ),
        start_state=0,
        accepted_states=is_final,
    )


def create_prefixed_led_and_button() -> NFA:
    """
    This example should be a sub-behavior of shuffling button with led-a.
    
    (0) LEDA.ON --->  (1)  BTN.PRS ----> (2)
        <--- LEDA.OFF      <--- BTN.REL
    """
    return NFA(
        # states=[0, 1, 2],
        alphabet=[LA_ON, LA_OFF, B_R, B_P],
        transition_func=NFA.transition_edges(
            [(0, [LA_ON], 1), (1, [LA_OFF], 0), (1, [B_P], 2), (2, [B_R], 1),]
        ),
        start_state=0,
        accepted_states=[0, 1, 2],
    )


def test_button() -> None:
    button = create_prefixed_button()
    assert button.accepts([])
    assert button.accepts([B_P, B_R])
    assert button.accepts([B_P])
    assert not button.accepts([B_R])


def test_shuffle() -> None:
    button = create_prefixed_button()
    led_a = create_prefixed_led_a()
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


def test_led_and_button() -> None:
    both = create_prefixed_led_and_button()
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


def test_contains() -> None:
    button = create_prefixed_button()
    led_a = create_prefixed_led_a()
    both = button.shuffle(led_a)
    behavior = create_prefixed_led_and_button()
    assert nfa_to_dfa(both).contains(nfa_to_dfa(behavior))


def test_hello_world() -> None:
    HELLO_WORLD_TRIGGERS = {
        LEVEL1: Concat.from_list(map(Char[str], [B_P, B_R, LA_ON, T_S])),
        LEVEL2: Concat.from_list(
            [Char(B_P), Char(B_R), And(Char(T_C), Char(LB_ON)), Char(T_S),]
        ),
        STANDBY1: concat(Char(T_T), Char(LA_OFF)),
        STANDBY2: concat(
            Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
            And(Char(LB_OFF), Char(LA_OFF)),
        ),
    }
    components = [
        create_prefixed_button(),
        create_prefixed_led_a(),
        create_prefixed_led_b(),
        create_prefixed_timer(),
    ]
    behavior = create_hello_world()
    be = automata.AssembledMicroBehavior.make(
        components, behavior, HELLO_WORLD_TRIGGERS
    )
    assert be.is_valid


def test_encode_1() -> None:
    behavior = Union(Char(LEVEL1), Star(Concat(Char(LEVEL1), Char(LEVEL2))))
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    be = nfa_to_dfa(automata.encode_behavior(regex_to_nfa(behavior), triggers))
    expected = nfa_to_dfa(regex_to_nfa(Star(Char(B_P)))).flatten(minimize=True)
    assert expected.contains(be)


def test_encode_behavior2_1() -> None:
    behavior = Union(Char(LEVEL1), Star(Concat(Char(LEVEL1), Char(LEVEL2))))
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    n_behavior = regex_to_nfa(behavior)
    expected = nfa_to_dfa(automata.encode_behavior(n_behavior, triggers))
    result = automata.MicroBehavior.make(n_behavior, triggers)
    assert result.is_valid
    given = result.dfa.minimize()
    assert given.is_equivalent_to(expected)


def test_encode2() -> None:
    behavior = Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    triggers = {
        LEVEL1: Concat(Char(B_P), Char(B_P)),
        LEVEL2: NIL,
    }
    be = nfa_to_dfa(automata.encode_behavior(regex_to_nfa(behavior), triggers))
    expected = nfa_to_dfa(regex_to_nfa(Star(Concat(Char(B_P), Char(B_P))))).flatten(
        minimize=True
    )
    assert expected.contains(be)
    assert be.contains(expected)


def test_ambiguity_1() -> None:
    behavior = Union(Char(LEVEL1), Star(Concat(Char(LEVEL1), Char(LEVEL2))))
    n_behavior = regex_to_nfa(behavior)
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    res = automata.AssembledMicroBehavior.make(
        [create_prefixed_button()], n_behavior, triggers
    )
    assert not res.micro.is_valid
    fail = res.micro.failure
    assert fail is not None
    assert fail.micro_trace == (B_P,)
    assert sorted(fail.macro_traces) == sorted([(LEVEL2,), (LEVEL1,)])


def test_ok_1() -> None:
    behavior = Union(Char(LEVEL1), Star(Concat(Char(LEVEL1), Char(LEVEL2))))
    n_behavior = regex_to_nfa(behavior)
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    assert automata.AssembledMicroBehavior.make(
        [create_prefixed_button()], n_behavior, triggers
    ).is_valid


def test_fail_hello_world() -> None:
    hello = create_hello_world()
    assert hello.accepts([])
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Concat.from_list(map(Char, [B_P, B_R, LA_ON, T_S])),
        LEVEL2: Concat.from_list(
            [Char(B_R), Char(B_P), And(Char(T_C), Char(LB_ON)), Char(T_S),]
        ),
        STANDBY1: concat(Char(T_T), Char(LA_OFF)),
        STANDBY2: concat(
            Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
            And(Char(LB_OFF), Char(LA_OFF)),
        ),
    }
    components = [
        create_prefixed_button(),
        create_prefixed_led_a(),
        create_prefixed_led_b(),
        create_prefixed_timer(),
    ]
    be = automata.encode_behavior(hello, triggers)
    assert be.accepts([])
    res = automata.AssembledMicroBehavior.make(components, hello, triggers)
    assert not res.is_valid
    assert not res.impossible.accepts(cast(List[str], []))


def test_smallest_error() -> None:
    hello = create_hello_world()
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Concat.from_list(
            map(Char, [B_P, B_P, LA_ON, T_S])  # <--- ERROR HERE: should be B_R
        ),
        LEVEL2: Concat.from_list(
            [
                Char(B_P),  #
                Char(B_R),  # Omitted string
                And(Char(T_C), Char(LB_ON)),
                Char(T_S),
            ]
        ),
        STANDBY1: concat(Char(T_T), Char(LA_OFF)),
        STANDBY2: concat(
            Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
            And(Char(LB_OFF), Char(LA_OFF)),
        ),
    }
    components = [
        create_prefixed_button(),
        create_prefixed_led_a(),
        create_prefixed_led_b(),
        create_prefixed_timer(),
    ]
    res = automata.AssembledMicroBehavior.make(components, hello, triggers)
    assert not res.is_valid
    assert res.micro.is_valid
    fail = res.impossible
    err = fail.get_shortest_string()
    assert err is not None
    assert fail.accepts(err)
    assert err is not None
    assert err == (B_P, B_P, LA_ON, T_S)
    assert automata.demultiplex(err) == {
        "b": ["pressed", "pressed"],
        "ledA": ["on"],
        "t": ["started"],
    }


def test_demultiplex() -> None:
    assert automata.demultiplex(["a.a1", "b.b1", "c.c1", "b.b2", "a.a2"]) == {
        "a": ["a1", "a2"],
        "b": ["b1", "b2"],
        "c": ["c1"],
    }


def test_prefix_nfa() -> None:
    led = NFA(
        alphabet=["on", "off"],
        transition_func=NFA.transition_edges([(0, ["on"], 1), (1, ["off"], 0),]),
        start_state=0,
        accepted_states=[0, 1],
    )
    assert automata.instantiate(led, "ledA.") == create_prefixed_led_a()


def test_build_components() -> None:
    led = NFA(
        alphabet=["on", "off"],
        transition_func=NFA.transition_edges([(0, ["on"], 1), (1, ["off"], 0),]),
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
    given = dict(automata.build_components(comps, known_devs))
    expected = {
        "ledA": create_prefixed_led_a(),
        "ledB": create_prefixed_led_b(),
    }
    assert expected == given
    assert len(expected) == len(given)
    for (ex, giv) in zip(expected, given):
        assert ex == giv


def test_build_components2() -> None:
    timer = NFA(
        # states=[0, 1],
        alphabet=["timeout", "canceled", "started"],
        transition_func=NFA.transition_edges(
            [(0, ["started"], 1), (1, ["canceled", "timeout"], 0),]
        ),
        start_state=0,
        accepted_states=[0, 1],
    )

    button = NFA(
        alphabet=["pressed", "released"],
        transition_func=NFA.transition_edges(
            [(0, ["pressed"], 1), (1, ["released"], 0),]
        ),
        start_state=0,
        accepted_states=[0, 1],
    )

    comps = {
        "t": "Timer",
        "b": "Button",
    }
    known_devs = {
        "Timer": CheckedDevice(timer),
        "Button": CheckedDevice(button),
    }
    given = dict(automata.build_components(comps, known_devs))
    expected = {
        "t": create_prefixed_timer(),
        "b": create_prefixed_button(),
    }
    assert expected == given
    assert len(expected) == len(given)
    for (ex, giv) in zip(expected, given):
        assert ex == giv


def test_build_nfa_transitions() -> None:
    start_events = ["level1"]
    behavior = [
        ("level1", "standby1"),
        ("level1", "level2"),
        ("level2", "standby2"),
        ("standby1", "level1"),
        ("standby2", "level1"),
    ]
    expected_tsx = {
        ("level1", "standby1"): {"standby1"},
        ("level1", "level2"): {"level2"},
        ("level2", "standby2"): {"standby2"},
        ("standby1", "level1"): {"level1"},
        ("standby2", "level1"): {"level1"},
        ("$START", "level1"): {"level1"},
    }

    actual_tsx = automata._build_nfa_transitions(behavior, start_events)

    assert actual_tsx == expected_tsx


def test_build_behavior() -> None:
    start_events = ["level1"]
    events = ["level1", "standby1", "level2", "standby2"]
    behavior = [
        ("level1", "standby1"),
        ("level1", "level2"),
        ("level2", "standby2"),
        ("standby1", "level1"),
        ("standby2", "level1"),
    ]
    tsx = [
        # Start events:
        ("start", "level1", "level1"),
        # (level1, standby1)
        ("level1", "standby1", "standby1"),
        ("level1", "level2", "level2"),
        ("level2", "standby2", "standby2"),
        ("standby1", "level1", "level1"),
        ("standby2", "level1", "level1"),
    ]
    accepted = set(x for x in events)
    accepted.add("start")
    expected = NFA(
        alphabet=set(events),
        transition_func=NFA.transition_edges_split(tsx),
        start_state="start",
        accepted_states=accepted,
    )
    assert (
        automata.build_external_behavior(behavior, start_events, events, "start")
        == expected
    )
    # Make sure this is equivalent to HELLO WORLD
    assert nfa_to_dfa(
        automata.build_external_behavior(behavior, start_events, events)
    ).is_equivalent_to(nfa_to_dfa(create_hello_world()))


def test_build_behavior_empty_start_events() -> None:
    with pytest.raises(ValueError) as exc_info:
        automata.build_external_behavior([], [], [], "start")

    assert str(exc_info.value) == "At least one start event must be specified."


def test_build_behavior_same_name_start_event() -> None:
    with pytest.raises(ValueError) as exc_info:
        automata.build_external_behavior([], ["xxx"], ["xxx", "yyy"], "yyy")

    assert (
        str(exc_info.value)
        == "Start state 'yyy' cannot have the same name as an event."
    )


######################
#### TEST DEVICES ####
######################


def test_device_button() -> None:
    device = Device(
        start_events=["b.pressed"],
        final_events=["b.pressed", "b.released"],
        events=["b.pressed", "b.released"],
        behavior=[("b.pressed", "b.released"), ("b.released", "b.pressed"),],
        components={},
        triggers={"b.pressed": NIL, "b.released": NIL,},
    )
    expected = AssembledDevice.make(device, {}).external.nfa.flatten()

    assert nfa_to_dfa(create_prefixed_button()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_led_a() -> None:
    device = Device(
        start_events=["ledA.on"],
        final_events=["ledA.on", "ledA.off"],
        events=["ledA.on", "ledA.off"],
        behavior=[("ledA.on", "ledA.off"), ("ledA.off", "ledA.on"),],
        components={},
        triggers={"ledA.on": NIL, "ledA.off": NIL,},
    )
    expected = AssembledDevice.make(device, {}).external.nfa.flatten()

    assert nfa_to_dfa(create_prefixed_led_a()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_led_b() -> None:
    device = Device(
        start_events=["ledB.on"],
        final_events=["ledB.on", "ledB.off"],
        events=["ledB.on", "ledB.off"],
        behavior=[("ledB.on", "ledB.off"), ("ledB.off", "ledB.on"),],
        components={},
        triggers={"ledB.on": NIL, "ledB.off": NIL,},
    )
    expected = AssembledDevice.make(device, {}).external.nfa.flatten()

    assert nfa_to_dfa(create_prefixed_led_b()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_timer() -> None:
    device = Device(
        start_events=["t.started"],
        final_events=["t.started", "t.canceled", "t.timeout"],
        events=["t.started", "t.canceled", "t.timeout"],
        behavior=[
            ("t.started", "t.canceled"),
            ("t.started", "t.timeout"),
            ("t.canceled", "t.started"),
            ("t.timeout", "t.started"),
        ],
        components={},
        triggers={"t.started": NIL, "t.canceled": NIL, "t.timeout": NIL},
    )
    expected = AssembledDevice.make(device, {}).external.nfa.flatten()

    assert nfa_to_dfa(create_prefixed_timer()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_hello_world() -> None:
    device = Device(
        start_events=["level1"],
        final_events=["level1", "level2", "standby1", "standby2"],
        events=["level1", "level2", "standby1", "standby2"],
        behavior=[
            ("level1", "standby1"),
            ("level1", "level2"),
            ("level2", "standby2"),
            ("standby1", "level1"),
            ("standby2", "level1"),
        ],
        components={},
        triggers={"level1": NIL, "level2": NIL, "standby1": NIL, "standby2": NIL},
    )
    expected = AssembledDevice.make(device, {}).external.nfa.flatten()

    assert nfa_to_dfa(create_hello_world()).is_equivalent_to(nfa_to_dfa(expected))


def get_basic_devices() -> Dict[str, Device]:
    return dict(
        Led=Device(
            start_events=["on"],
            final_events=["on", "off"],
            events=["on", "off"],
            behavior=[("on", "off"), ("off", "on"),],
            components={},
            triggers={"on": NIL, "off": NIL,},
        ),
        Button=Device(
            start_events=["pressed"],
            final_events=["pressed", "released"],
            events=["pressed", "released"],
            behavior=[("pressed", "released"), ("released", "pressed"),],
            components={},
            triggers={"pressed": NIL, "released": NIL,},
        ),
        Timer=Device(
            start_events=["started"],
            final_events=["started", "canceled", "timeout"],
            events=["started", "canceled", "timeout"],
            behavior=[
                ("started", "canceled"),
                ("started", "timeout"),
                ("canceled", "started"),
                ("timeout", "started"),
            ],
            components={},
            triggers={"started": NIL, "canceled": NIL, "timeout": NIL},
        ),
    )


def get_basic_known_devices() -> Dict[str, CheckedDevice]:
    return dict(
        (k, AssembledDevice.make(d, {}).external)
        for (k, d) in get_basic_devices().items()
    )


def test_invalid_behavior_1() -> None:
    device = Device(
        start_events=["level1"],
        final_events=["level1", "level2", "standby1", "standby2"],
        events=["level1", "level2", "standby1", "standby2"],
        behavior=[
            ("level1", "standby1"),
            ("level1", "level2"),
            ("level2", "standby2"),
            ("standby1", "level1"),
            ("standby2", "level1"),
        ],
        components={"b": "Button", "ledA": "Led", "ledB": "Led", "t": "Timer",},
        triggers={
            LEVEL1: Concat.from_list(
                map(Char, [B_P, B_P, LA_ON, T_S])  # <--- ERROR HERE: should be B_R
            ),
            LEVEL2: Concat.from_list(
                [Char(B_P), Char(B_R), And(Char(T_C), Char(LB_ON)), Char(T_S),]
            ),
            STANDBY1: concat(Char(T_T), Char(LA_OFF)),
            STANDBY2: concat(
                Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                And(Char(LB_OFF), Char(LA_OFF)),
            ),
        },
    )
    given = AssembledDevice.make(device, get_basic_known_devices())
    assert not given.is_valid
    assert isinstance(given.failure, automata.TriggerIntegrationFailure)
    assert given.failure.macro_trace == (LEVEL1,)
    assert given.failure.micro_trace == (B_P, B_P, LA_ON, T_S)
    assert given.failure.component_errors == {
        "b": (("pressed", "pressed"), 1),
    }


def test_invalid_behavior_2() -> None:
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Concat.from_list(
            map(
                Char,
                [
                    B_R,  # <--- ERROR HERE: should be B_P
                    B_P,  # <--- ERROR HERE: should be B_P
                    B_R,  # <--- ERROR HERE: should be B_P
                    LA_ON,
                    T_S,
                ],
            )
        ),
        LEVEL2: Concat.from_list(
            [Char(B_P), Char(B_R), And(Char(T_C), Char(LB_ON)), Char(T_S),]
        ),
        STANDBY1: concat(Char(T_T), Char(LA_OFF)),
        STANDBY2: concat(
            Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
            And(Char(LB_OFF), Char(LA_OFF)),
        ),
    }

    device = Device(
        start_events=["level1"],
        final_events=["level1", "level2", "standby1", "standby2"],
        events=["level1", "level2", "standby1", "standby2"],
        behavior=[
            ("level1", "standby1"),
            ("level1", "level2"),
            ("level2", "standby2"),
            ("standby1", "level1"),
            ("standby2", "level1"),
        ],
        components={"b": "Button", "ledA": "Led", "ledB": "Led", "t": "Timer",},
        triggers=triggers,
    )
    given = AssembledDevice.make(device, get_basic_known_devices())
    assert not given.is_valid
    assert isinstance(given.failure, automata.TriggerIntegrationFailure)
    assert given.failure.micro_trace == (B_R, B_P, B_R, LA_ON, T_S)
    assert given.failure.macro_trace == (LEVEL1,)
    assert given.failure.component_errors == {
        "b": (("released", "pressed", "released"), 0),
    }


def test_device_led_and_button() -> None:
    device = Device(
        start_events=["ledA.on"],
        final_events=["ledA.on", "ledA.off", "b.pressed", "b.released"],
        events=["ledA.on", "ledA.off", "b.pressed", "b.released"],
        behavior=[
            ("ledA.on", "ledA.off"),
            ("ledA.on", "b.pressed"),
            ("b.pressed", "b.released"),
            ("b.released", "ledA.off"),
            ("b.released", "b.pressed"),
            ("ledA.off", "ledA.on"),
        ],
        components={},
        triggers={"ledA.on": NIL, "ledA.off": NIL, "b.pressed": NIL, "b.released": NIL},
    )
    expected = AssembledDevice.make(device, {}).external.nfa.flatten()

    assert nfa_to_dfa(create_prefixed_led_and_button()).is_equivalent_to(
        nfa_to_dfa(expected)
    )
