import pytest
from typing import Dict, cast, List, Any, Callable
from karakuri.regular import (
    NFA,
    DFA,
    regex_to_nfa,
    Union,
    Char,
    Concat,
    concat,
    shuffle as And,
    nfa_to_dfa,
    dfa_to_nfa,
    Star,
    NIL,
    Regex,
)
from shelley.automata import (
    Device,
    AssembledDevice,
    CheckedDevice,
    AssembledMicroBehavior2,
    project_nfa,
    ComponentUsageFailure,
    pad_trace,
    Component,
)
from shelley import automata

B_P: str = "b.pressed"
B_R: str = "b.released"


def create_led_nfa() -> NFA[Any, str]:
    # fmt: off
    return NFA(
        alphabet=["on", "off"],
        transition_func=NFA.transition_edges(
            [
                (0, ["on"], 1),
                (1, ["off"], 2),
                (2, ["on"], 1),
            ]
        ),
        start_state=0,
        accepted_states=[1, 2],
    )
    # fmt: on


def create_led_dev() -> CheckedDevice:
    return CheckedDevice(create_led_nfa())


def create_button_nfa() -> NFA[Any, str]:
    # fmt: off
    return NFA(
        alphabet=["pressed", "released"],
        transition_func=NFA.transition_edges(
            [
                (0, ["pressed"], 1),
                (1, ["released"], 2),
                (2, ["pressed"], 1),
            ]
        ),
        start_state=0,
        accepted_states=[2, 1],
    )
    # fmt: on


def create_button_dev() -> CheckedDevice:
    return CheckedDevice(create_button_nfa())


def create_timer_nfa() -> NFA[Any, str]:
    # fmt: off
    return NFA(
        alphabet=["timeout", "canceled", "started"],
        transition_func=NFA.transition_edges(
            [
                (0, ["started"], 1),
                (1, ["canceled", "timeout"], 2),
                (2, ["started"], 1),
            ]
        ),
        start_state=0,
        accepted_states=[2, 1],
    )
    # fmt: on


def create_timer_dev() -> CheckedDevice:
    return CheckedDevice(create_timer_nfa())


def create_button_b_nfa() -> NFA:
    # fmt: off
    return NFA(
        alphabet=[B_P, B_R],
        transition_func=NFA[int, str].transition_edges(
            [
                (0, set([B_P]), 1),
                (1, set([B_R]), 2),
                (2, set([B_P]), 1),
            ]
        ),
        start_state=0,
        accepted_states=[1, 2],
    )
    # fmt: on


def test_button() -> None:
    button = create_button_b_nfa()
    assert button.accepts([B_P, B_R])
    assert button.accepts([B_P])
    assert not button.accepts([B_R])


def create_button_b() -> Component:
    return Component("b", create_button_dev())


LA_ON = "ledA.on"
LA_OFF = "ledA.off"


def create_led_a_nfa() -> NFA:
    # fmt: off
    return NFA(
        alphabet=[LA_ON, LA_OFF],
        transition_func=NFA.transition_edges(
            [
                (0, [LA_ON], 1),
                (1, [LA_OFF], 2),
                (2, [LA_ON], 1),
            ]
        ),
        start_state=0,
        accepted_states=[1, 2],
    )
    # fmt: on


def create_led_a() -> Component:
    return Component("ledA", create_led_dev())


LB_ON = "ledB.on"
LB_OFF = "ledB.off"


def create_led_b_nfa() -> NFA:
    # fmt: off
    return NFA(
        alphabet=[LB_ON, LB_OFF],
        transition_func=NFA.transition_edges(
            [
                (0, [LB_ON], 1),
                (1, [LB_OFF], 2),
                (2, [LB_ON], 1),
            ]
        ),
        start_state=0,
        accepted_states=[1, 2],
    )
    # fmt: on


def create_led_b() -> Component:
    return Component("ledB", create_led_dev())


T_T = "t.timeout"
T_C = "t.canceled"
T_S = "t.started"


def create_timer_t_nfa() -> NFA:
    return NFA(
        alphabet=[T_T, T_C, T_S],
        transition_func=NFA.transition_edges(
            [(0, [T_S], 1), (1, [T_C, T_T], 2), (2, [T_S], 1),]  #  #  #  #
        ),
        start_state=0,
        accepted_states=[1, 2],
    )


def create_timer_t() -> Component:
    return Component("t", create_timer_dev())


LEVEL1 = "level1"
LEVEL2 = "level2"
STANDBY1 = "standby1"
STANDBY2 = "standby2"


def create_hello_world_nfa() -> NFA:
    return NFA(
        alphabet=[LEVEL1, LEVEL2, STANDBY1, STANDBY2],
        transition_func=NFA.transition_edges(
            [
                (0, [LEVEL1], 1),
                (1, [LEVEL2], 2),
                (1, [STANDBY1], 3),
                (2, [STANDBY2], 3),
                (3, [LEVEL1], 1),
            ]
        ),
        start_state=0,
        accepted_states=[1, 2, 3],
    )


def create_hello_world_dev() -> CheckedDevice:
    return CheckedDevice(create_hello_world_nfa())


def create_prefixed_led_and_button() -> NFA:
    """
    This example should be a sub-behavior of shuffling button with led-a.
    
    (0) LEDA.ON --->  (1)  BTN.PRS ----> (2)
        <--- LEDA.OFF      <--- BTN.REL
    """
    return NFA(
        alphabet=[LA_ON, LA_OFF, B_R, B_P],
        transition_func=NFA.transition_edges(
            [
                (0, [LA_ON], 1),
                (1, [LA_OFF], 3),
                (1, [B_P], 2),
                (2, [B_R], 1),
                (3, [LA_ON], 1),
            ]
        ),
        start_state=0,
        accepted_states=[1, 2, 3],
    )


def test_shuffle() -> None:
    button = create_button_b_nfa()
    led_a = create_led_a_nfa()
    both = button.shuffle(led_a)
    # Both should accept all behaviors of the button
    assert button.accepts([B_P, B_R])
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
    button = create_button_b_nfa()
    led_a = create_led_a_nfa()
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
        create_button_b(),
        create_led_a(),
        create_led_b(),
        create_timer_t(),
    ]
    behavior = create_hello_world_nfa()
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
    expected = nfa_to_dfa(regex_to_nfa(Star(Char(B_P))))
    assert expected.contains(be)


def test_encode_behavior2_1() -> None:
    l1_l2 = Concat(Char(LEVEL1), Char(LEVEL2))
    behavior = Union(Char(LEVEL1), Concat(l1_l2, Star(l1_l2)))
    n_behavior = dfa_to_nfa(nfa_to_dfa(regex_to_nfa(behavior)).minimize())
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    expected = nfa_to_dfa(automata.encode_behavior(n_behavior, triggers))
    result = automata.MicroBehavior.make(n_behavior, triggers, set(expected.alphabet))
    assert result.is_valid
    assert_equiv_dfa(expected, result.dfa)


def test_encode2() -> None:
    behavior = Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    triggers = {
        LEVEL1: Concat(Char(B_P), Char(B_P)),
        LEVEL2: NIL,
    }
    be = nfa_to_dfa(automata.encode_behavior(regex_to_nfa(behavior), triggers))
    expected = nfa_to_dfa(regex_to_nfa(Star(Concat(Char(B_P), Char(B_P)))))
    assert expected.contains(be)
    assert be.contains(expected)


def test_ambiguity_1() -> None:
    behavior = Union(Char(LEVEL1), Star(Concat(Char(LEVEL1), Char(LEVEL2))))
    n_behavior = dfa_to_nfa(nfa_to_dfa(regex_to_nfa(behavior)).minimize())
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    res = automata.AssembledMicroBehavior.make(
        [create_button_b()], n_behavior, triggers
    )
    assert not res.micro.is_valid
    fail = res.micro.failure
    assert fail is not None
    assert fail.micro_trace == (B_P,)
    assert sorted(fail.macro_traces) == sorted([(LEVEL2,), (LEVEL1,)])


def test_ok_1() -> None:
    behavior = Union(
        Char(LEVEL1),
        Concat(
            Concat(Char(LEVEL1), Char(LEVEL2)), Star(Concat(Char(LEVEL1), Char(LEVEL2)))
        ),
    )
    n_behavior = regex_to_nfa(behavior)
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    assert automata.AssembledMicroBehavior.make(
        [create_button_b()], n_behavior, triggers
    ).is_valid


def test_fail_hello_world() -> None:
    hello = create_hello_world_nfa()
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
        create_button_b(),
        create_led_a(),
        create_led_b(),
        create_timer_t(),
    ]
    be = automata.encode_behavior(hello, triggers)
    res = automata.AssembledMicroBehavior.make(components, hello, triggers)
    assert not res.is_valid
    assert not res.impossible.accepts(cast(List[str], []))


def test_smallest_error() -> None:
    hello = create_hello_world_nfa()
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
        create_button_b(),
        create_led_a(),
        create_led_b(),
        create_timer_t(),
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
    led = create_led_nfa()
    assert automata.instantiate(led, "ledA.") == create_led_a_nfa()


def test_components() -> None:
    led = create_led_dev()
    btn = create_button_dev()
    tmr = create_timer_dev()

    led_a = Component("ledA", led)
    assert led_a.behavior == create_led_a_nfa()
    led_b = Component("ledB", led)
    assert led_b.behavior == create_led_b_nfa()
    b = Component("b", btn)
    assert b.behavior == create_button_b_nfa()
    t = Component("t", tmr)
    assert t.behavior == create_timer_t_nfa()


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
    final_events = ["level1", "standby1", "level2", "standby2"]
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
    # accepted.add("start")
    expected = NFA(
        alphabet=set(events),
        transition_func=NFA.transition_edges_split(tsx),
        start_state="start",
        accepted_states=accepted,
    )
    assert (
        automata.build_external_behavior(
            behavior, start_events, final_events, events, "start"
        )
        == expected
    )
    # Make sure this is equivalent to HELLO WORLD
    assert nfa_to_dfa(
        automata.build_external_behavior(behavior, start_events, final_events, events)
    ).is_equivalent_to(nfa_to_dfa(create_hello_world_nfa()))


def test_build_behavior_empty_start_events() -> None:
    with pytest.raises(ValueError) as exc_info:
        automata.build_external_behavior([], [], [], [], "start")

    assert str(exc_info.value) == "At least one start event must be specified."


def test_build_behavior_same_name_start_event() -> None:
    with pytest.raises(ValueError) as exc_info:
        automata.build_external_behavior(
            [], ["xxx"], ["xxx", "yyy"], ["xxx", "yyy"], "yyy"
        )

    assert (
        str(exc_info.value)
        == "Start state 'yyy' cannot have the same name as an event."
    )


######################
#### TEST DEVICES ####
######################


def empty_devices(name: str) -> CheckedDevice:
    raise ValueError()


def test_device_button() -> None:
    device = Device(
        start_events=["b.pressed"],
        final_events=["b.pressed", "b.released"],
        events=["b.pressed", "b.released"],
        behavior=[("b.pressed", "b.released"), ("b.released", "b.pressed"),],
        components={},
        triggers={"b.pressed": NIL, "b.released": NIL,},
    )
    expected = AssembledDevice.make(device, empty_devices).external.nfa

    assert nfa_to_dfa(create_button_b_nfa()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_led_a() -> None:
    device = Device(
        start_events=["ledA.on"],
        final_events=["ledA.on", "ledA.off"],
        events=["ledA.on", "ledA.off"],
        behavior=[("ledA.on", "ledA.off"), ("ledA.off", "ledA.on"),],
        components={},
        triggers={"ledA.on": NIL, "ledA.off": NIL,},
    )
    expected = AssembledDevice.make(device, empty_devices).external.nfa

    assert nfa_to_dfa(create_led_a_nfa()).is_equivalent_to(nfa_to_dfa(expected))


def test_device_led_b() -> None:
    device = Device(
        start_events=[LB_ON],
        final_events=[LB_ON, LB_OFF],
        events=[LB_ON, LB_OFF],
        behavior=[(LB_ON, LB_OFF), (LB_OFF, LB_ON),],
        components={},
        triggers={LB_ON: NIL, LB_OFF: NIL,},
    )
    expected = AssembledDevice.make(device, empty_devices).external.nfa

    assert nfa_to_dfa(create_led_b_nfa()).is_equivalent_to(nfa_to_dfa(expected))


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
    expected = AssembledDevice.make(device, empty_devices).external.nfa

    assert nfa_to_dfa(create_timer_t_nfa()).is_equivalent_to(nfa_to_dfa(expected))


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
    expected = AssembledDevice.make(device, empty_devices).external.nfa

    assert nfa_to_dfa(create_hello_world_nfa()).is_equivalent_to(nfa_to_dfa(expected))


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


def get_basic_known_devices() -> Callable[[str], CheckedDevice]:
    return dict(
        (k, AssembledDevice.make(d, empty_devices).external)
        for (k, d) in get_basic_devices().items()
    ).__getitem__


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


def test_pad_trace_1() -> None:
    given = pad_trace(tuple(["a", "b"]), ["c"])
    expected = NFA(
        alphabet=["a", "b", "c"],
        transition_func=NFA.transition_table(
            {
                (0, "a"): frozenset([1]),
                (1, "b"): frozenset([2]),
                (0, "c"): frozenset([0]),
                (1, "c"): frozenset([1]),
                (2, "c"): frozenset([2]),
            }
        ),
        start_state=0,
        accepted_states=[2],
    )
    assert given == expected


def test_pad_trace_2() -> None:
    given = pad_trace(tuple(["a", "b"]), ["c", "d"])
    expected = NFA(
        alphabet=["a", "b", "c", "d"],
        transition_func=NFA.transition_table(
            {
                (0, "a"): frozenset([1]),
                (1, "b"): frozenset([2]),
                (0, "c"): frozenset([0]),
                (1, "c"): frozenset([1]),
                (2, "c"): frozenset([2]),
                (0, "d"): frozenset([0]),
                (1, "d"): frozenset([1]),
                (2, "d"): frozenset([2]),
            }
        ),
        start_state=0,
        accepted_states=[2],
    )
    assert given == expected


def test_pad_trace_3() -> None:
    # 1. Compute the set of characters to pad
    pad_alpha = {T_C, T_S, T_T, LA_OFF, LA_ON, LB_OFF, LB_ON}
    # 2. Find the set of all padded strings
    trace_dfa = nfa_to_dfa(pad_trace(trace=(B_R, B_P, B_R), alphabet=pad_alpha))
    # 3. Find the set of padded strings that are in the micro
    assert [B_R, B_P, B_R, LA_ON, T_S,] in trace_dfa


def test_invalid_behavior_2() -> None:
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Concat.from_list(
            map(Char, [B_R, B_P, B_R, LA_ON, T_S,],)  # <--- ERROR HERE: should be B_P
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
    fast_check = AssembledDevice.make(
        device, get_basic_known_devices(), fast_check=True
    )
    assert isinstance(fast_check.internal, AssembledMicroBehavior2)
    assert not fast_check.is_valid


def test_get_traces_from_components() -> None:
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Concat.from_list(
            map(Char, [B_R, B_P, B_R, LA_ON, T_S,],)  # <--- ERROR HERE: should be B_P
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
    assert given.internal is not None
    micro = given.internal.micro

    # 1. Compute the set of characters to pad
    pad_alpha = {T_C, T_S, T_T, LA_OFF, LA_ON, LB_OFF, LB_ON}
    # 2. Find the set of all padded strings
    trace_dfa = nfa_to_dfa(pad_trace(trace=(B_R, B_P, B_R), alphabet=pad_alpha))
    # 3. Find the set of padded strings that are in the micro
    assert [B_R, B_P, B_R, LA_ON, T_S,] in trace_dfa

    invalid1 = micro.get_traces_from_component_trace({B_R, B_P}, (B_R, B_P, B_R))
    assert [B_R, B_P, B_R, LA_ON, T_S,] in invalid1
    assert not invalid1.is_empty()
    invalid2 = invalid1.set_alphabet(micro.dfa.alphabet)
    assert [B_R, B_P, B_R, LA_ON, T_S,] in invalid2
    assert not invalid2.is_empty()
    invalid3 = micro.dfa.intersection(invalid2)
    assert [B_R, B_P, B_R, LA_ON, T_S,] in invalid3
    assert not invalid3.is_empty()


def test_projection_2() -> None:
    expected_nfa = NFA[int, str](
        alphabet=["b.pressed", "b.released"],
        transition_func=NFA.transition_table(
            {(0, "b.released"): frozenset([1]), (1, "b.pressed"): frozenset([2]),}
        ),
        accepted_states=[0, 1, 2],
        start_state=0,
    )

    def tsx(st, a):
        if st == 0:
            if a == B_P:
                return 3
            elif a == B_R:
                return 1
        elif st == 1:
            if a == B_P:
                return 2
            elif a == B_R:
                return 3
        elif st == 2 or st == 3:
            if a == B_P or a == B_R:
                return 3
        raise ValueError(st, a)

    expected_dfa = DFA[int, str]([B_P, B_R], tsx, 0, [0, 1, 2])
    assert expected_dfa.is_equivalent_to(nfa_to_dfa(expected_nfa))
    assert [B_R, B_P] in expected_dfa
    assert [B_P, B_R] not in expected_dfa
    assert expected_nfa == project_nfa(expected_nfa, expected_nfa.alphabet)


def test_projection_class() -> None:
    micro_nfa = NFA[int, str](
        alphabet=[B_P, B_R],
        transition_func=NFA.transition_table(
            {(0, B_R): frozenset([1]), (1, B_P): frozenset([2]),}
        ),
        accepted_states=[1, 2],
        start_state=0,
    )
    micro_dfa = nfa_to_dfa(micro_nfa)
    button_nfa = create_button_b_nfa()
    button_dfa = nfa_to_dfa(button_nfa)
    # We build a projection directly
    proj = ComponentUsageFailure.make(micro_nfa, button_nfa)
    assert project_nfa(micro_nfa, button_nfa.alphabet) == micro_nfa
    assert proj.component == button_dfa, "component was set incorrectly"
    assert_equiv_dfa(proj.projected, micro_dfa, "projected was set incorrectly")
    assert not proj.is_valid


def assert_equiv_nfa(self: NFA[Any, str], other: NFA[Any, str]):
    assert_equiv_dfa(nfa_to_dfa(self), nfa_to_dfa(other))


def assert_equiv_dfa(lhs: DFA[Any, str], rhs: DFA[Any, str], msg=""):
    if msg != "":
        msg = f"{msg}: "
    missing = lhs.subtract(rhs)

    def log_accept(lbl: str, d: DFA[Any, str], err: List[str]) -> None:
        msg = "accept" if err in d else "reject"
        print(f"{lbl} {msg} {err}")

    if not missing.is_empty():
        err_l = missing.get_shortest_string()
        assert err_l is not None
        err = list(err_l)
        log_accept(f"lhs", lhs, err)
        log_accept(f"rhs", rhs, err)
        print("LHS:", lhs.minimize())
        print("RHS:", rhs.minimize())
        assert False, f"{msg}rhs REJECTS string: {err}"
    missing = rhs.subtract(lhs)
    if not missing.is_empty():
        err_l = missing.get_shortest_string()
        assert err_l is not None
        err = list(err_l)
        log_accept(f"lhs", lhs, err)
        log_accept(f"rhs", rhs, err)
        print(lhs)
        print(rhs)
        assert False, f"{msg}lhs REJECTS string: {err}"


def test_invalid_behavior_4() -> None:
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Char(B_R),
        LEVEL2: Char(B_P),
    }
    device = Device(
        start_events=["level1"],
        final_events=["level1", "level2",],
        events=["level1", "level2",],
        behavior=[("level1", "level2"),],
        components={"b": "Button",},
        triggers=triggers,
    )
    given = AssembledDevice.make(device, get_basic_known_devices())
    assert not given.is_valid
    ################################################
    # Let us make sure we get the internal behaviour
    # This is the expected internal NFA:
    micro_nfa = NFA[int, str](
        alphabet=[B_P, B_R],
        transition_func=NFA.transition_table(
            {(0, B_R): frozenset([1]), (1, B_P): frozenset([2]),}  #  #  #
        ),
        accepted_states=[1, 2],
        start_state=0,
    )
    micro_dfa = nfa_to_dfa(micro_nfa)
    assert given.internal is not None
    assert given.internal.dfa.is_equivalent_to(micro_dfa)
    ################################################
    # Now that we checked our assumptions let us setup the fast algorithm:
    fast_check = AssembledDevice.make(
        device, get_basic_known_devices(), fast_check=True
    )
    assert isinstance(fast_check.internal, AssembledMicroBehavior2)
    ################################################
    # 1. The internal behaviour should remain the same
    assert fast_check.internal.dfa.is_equivalent_to(
        micro_dfa
    ), "micro behaviour with fast-check should remain the same"
    ################################################
    # 2. We now test the projected button
    proj_btn = fast_check.internal.usages["b"]
    ################################################
    # 2.1 We test if componet for button was correctly initialized
    # The NFA below should represent the Button instantiated with 'b':
    button_nfa = create_button_b_nfa()
    button_dfa = nfa_to_dfa(button_nfa)
    ################################################
    # We build a projection directly
    # Test if the component was set correctly
    assert_equiv_nfa(
        project_nfa(given.internal.nfa, button_nfa.alphabet), given.internal.nfa
    )
    assert_equiv_dfa(
        proj_btn.component,
        button_dfa,
        "(proj_btn, button_dfa): projected button differs from button",
    )
    assert_equiv_dfa(proj_btn.projected, micro_dfa, "projected was set incorrectly")
    converted = nfa_to_dfa(project_nfa(micro_nfa, button_nfa.alphabet))
    assert converted.is_equivalent_to(proj_btn.projected)
    ################################################
    # 2.3 Next we test the projected DFA
    assert proj_btn.projected.is_equivalent_to(
        micro_dfa
    ), "projection should not alter the behaviour"
    ################################################
    # Finally the result should not be valid
    assert not fast_check.is_valid


def test_invalid_behavior_3() -> None:
    # Projected triggers to Button
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Concat.from_list(
            map(Char, [B_R, B_P, B_R,],)  # <--- ERROR HERE: should be B_P
        ),
        LEVEL2: Concat.from_list([Char(B_P), Char(B_R),]),
        STANDBY2: Concat.from_list(map(Char, [B_P, B_R])),
    }

    device = Device(
        start_events=["level1"],
        final_events=["level1", "level2", "standby2"],
        events=["level1", "level2", "standby2"],
        behavior=[
            ("level1", "level2"),
            ("level2", "standby2"),
            ("standby2", "level1"),
        ],
        components={"b": "Button",},
        triggers=triggers,
    )
    given = AssembledDevice.make(device, get_basic_known_devices())
    assert not given.is_valid
    fast_check = AssembledDevice.make(
        device, get_basic_known_devices(), fast_check=True
    )
    assert isinstance(fast_check.internal, AssembledMicroBehavior2)
    assert not fast_check.is_valid


def test_valid_behavior_3() -> None:
    # Projected triggers to Button
    triggers: Dict[str, Regex[str]] = {
        LEVEL1: Concat.from_list(map(Char, [B_P, B_R, B_P, B_R,],)),
    }

    device = Device(
        start_events=["level1"],
        final_events=["level1"],
        events=["level1"],
        behavior=[],
        components={"b": "Button",},
        triggers=triggers,
    )
    given = AssembledDevice.make(device, get_basic_known_devices())
    assert given.is_valid
    fast_check = AssembledDevice.make(
        device, get_basic_known_devices(), fast_check=True
    )
    assert isinstance(fast_check.internal, AssembledMicroBehavior2)
    assert fast_check.is_valid


def test_projection() -> None:
    n1 = NFA(
        alphabet="abc",
        transition_func=NFA.transition_table(
            {
                (0, "a"): frozenset([0, 2]),
                (0, "b"): frozenset([3]),
                (0, "c"): frozenset([1]),
                (1, "a"): frozenset([0]),
                (1, "c"): frozenset([3]),
                (2, "b"): frozenset([3]),
                (3, "a"): frozenset([3]),
                (3, "c"): frozenset([1]),
            }
        ),
        start_state=0,
        accepted_states=[2],
    )
    given = project_nfa(n1, "ac")
    expected = NFA(
        alphabet="abc",
        transition_func=NFA.transition_table(
            {
                (0, "a"): frozenset([0, 2]),
                (0, None): frozenset([3]),
                (0, "c"): frozenset([1]),
                (1, "a"): frozenset([0]),
                (1, "c"): frozenset([3]),
                (2, None): frozenset([3]),
                (3, "a"): frozenset([3]),
                (3, "c"): frozenset([1]),
            }
        ),
        start_state=0,
        accepted_states=[2],
    )
    assert expected == given


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
    expected = AssembledDevice.make(device, empty_devices).external.nfa
    assert_equiv_nfa(create_prefixed_led_and_button(), expected)
