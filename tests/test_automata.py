#from .context import shelley

from karakuri.regular import NFA, DFA, Nil, nfa_to_regex, regex_to_nfa, Union, Char, Concat, concat, shuffle as And, nfa_to_dfa, Star
from shelley.automata import check_valid, replace, decode_behavior

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
        alphabet=[LA_ON, LA_OFF],
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
    assert check_valid(components, nfa_to_regex(behavior), HELLO_WORLD_TRIGGERS)

def test_decode_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    be = decode_behavior(behavior, triggers, flatten=True, minimize=True)
    expected = nfa_to_dfa(regex_to_nfa(Star(Char(B_P)))).flatten(minimize=True)
    assert expected.contains(be)
    assert be.contains(expected)

def test_decode2():
    behavior = Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    triggers = {
        LEVEL1: Concat(Char(B_P),Char(B_P)),
        LEVEL2: Nil,
    }
    be = decode_behavior(behavior, triggers, flatten=True, minimize=True)
    expected = nfa_to_dfa(regex_to_nfa(Star(Concat(Char(B_P),Char(B_P))))).flatten(minimize=True)
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
    assert not check_valid([create_button()], behavior, triggers)

def test_ok_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    assert check_valid([create_button()], behavior, triggers)

def test_fail_hello_world():
    behavior = nfa_to_regex(create_hello_world())
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
    assert not check_valid(components, behavior, triggers)