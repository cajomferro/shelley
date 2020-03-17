#from .context import shelley

from karakuri.regular import NFA, DFA, nfa_to_regex, regex_to_nfa, Union, Char, Concat, concat, shuffle as And, nfa_to_dfa
from shelley.automata import check_valid, replace

B_P = "b.pressed"
B_R = "b.release"


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


LA_ON = "la.on"
LA_OFF = "la.off"


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


LB_ON = "lb.on"
LB_OFF = "lb.off"


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


T_T = "t.t"
T_C = "t.c"
T_S = "t.s"


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


LEVEL1 = "l1"
LEVEL2 = "l2"
STANDBY1 = "s1"
STANDBY2 = "s2"
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


def create_hello_world():
    return NFA(
        # states=[0, 1, 2],
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
    components = [
        create_button(),
        create_led_a(),
        create_led_b(),
        create_timer()
    ]
    behavior = create_hello_world()
    assert check_valid(components, behavior, HELLO_WORLD_TRIGGERS)


def test_fail_hello_world():
    HELLO_WORLD_TRIGGERS = {
        LEVEL1:
            Concat.from_list(map(Char, [B_P, B_R, LA_ON, T_S])),
        LEVEL2:
            Concat.from_list([
                Char(B_P),
                # Char(B_R),
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
    assert not check_valid(components, behavior, HELLO_WORLD_TRIGGERS)


# test_minimize()
test_hello_world()
