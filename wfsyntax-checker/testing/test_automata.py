import unittest

from dfaapp import app
from dfaapp.automaton import NFA
from dfaapp.regex import nfa_to_regex, regex_to_nfa, Union, Char, Concat, concat, op_and as And
from dfaapp.checker import check_valid, replace

B_P = "b.pressed"
B_R = "b.release"

def create_button():
    return NFA(
        states=[0, 1],
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
        states=[0, 1],
        alphabet=[LA_ON, LA_OFF],
        transition_func=NFA.transition_edges([
            (0, [LA_ON], 1),
            (1, [LA_OFF], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )

def test_button():
    button = create_button()
    assert button.accepts([])
    assert button.accepts([B_P,B_R])
    assert button.accepts([B_P])
    assert not button.accepts([B_R])

def test_convert_dfa():
    button = create_button()
    button = button.convert_to_dfa()
    assert button.accepts([])
    assert button.accepts([B_P,B_R])
    assert button.accepts([B_P])
    assert not button.accepts([B_R])

def test_complement():
    """
    A simple test on the complement of a DFA
    """
    button = create_button()
    button = button.convert_to_dfa()
    button = button.complement()
    assert not button.accepts([])
    assert not button.accepts([B_P,B_R])
    assert not button.accepts([B_P])
    assert button.accepts([B_R])

def test_shuffle():
    button = create_button()
    led_a = create_led_a()
    both = button.shuffle(led_a)
    # Both should accept all behaviors of the button
    assert both.accepts([])
    assert both.accepts([B_P,B_R])
    assert both.accepts([B_P])
    assert not both.accepts([B_R])
    # It should also accept all behaviors of led
    assert both.accepts([LA_ON,LA_OFF])
    assert both.accepts([LA_ON])
    assert not both.accepts([LA_OFF])
    # Finally, it should accept interleaving of LED and Button:
    assert both.accepts([LA_ON,B_P,B_R, LA_OFF,B_P])
    # Here we fail because we have B_P followed by B_P
    assert not both.accepts([LA_ON,B_P,LA_OFF,B_P])


def run(dest_path: str):
    with app.run(dest_path) as fs:
        def L(x):
            return "{\\tt " + x + "}"

        B_P = L("b.p")
        B_R = L("b.r")

        B = NFA(
            states=[0, 1],
            alphabet=[B_P, B_R],
            transition_func=NFA.transition_edges([
                (0, [B_P], 1),
                (1, [B_R], 0),
            ]),
            start_state=0,
            accepted_states=[0, 1],
        )
        fs.save_nfa_dot(B, "button")

        LA_ON = L("la.on")
        LA_OFF = L("la.off")
        LA = NFA(
            states=[0, 1],
            alphabet=[LA_ON, LA_OFF],
            transition_func=NFA.transition_edges([
                (0, [LA_ON], 1),
                (1, [LA_OFF], 0),
            ]),
            start_state=0,
            accepted_states=[0, 1],
        )
        fs.save_nfa_dot(LA, "led-a")

        LB_ON = L("lb.on")
        LB_OFF = L("lb.off")
        LB = NFA(
            states=[0, 1],
            alphabet=[LB_ON, LB_OFF],
            transition_func=NFA.transition_edges([
                (0, [LB_ON], 1),
                (1, [LB_OFF], 0),
            ]),
            start_state=0,
            accepted_states=[0, 1],
        )
        fs.save_nfa_dot(LA, "led-b")

        T_T = L("t.t")
        T_C = L("t.c")
        T_S = L("t.s")
        T = NFA(
            states=[0, 1],
            alphabet=[T_T, T_C, T_S],
            transition_func=NFA.transition_edges([
                (0, [T_S], 1),
                (1, [T_C, T_T], 0),
            ]),
            start_state=0,
            accepted_states=[0, 1],
        )
        fs.save_nfa_dot(T, "timer")

        # Merge all

        def render_state_name(st):
            elems = []
            to_proc = [st]
            while len(to_proc) > 0:
                st = to_proc.pop()
                if isinstance(st, int):
                    elems.append(st)
                elif isinstance(st, str):
                    elems.append(st)
                else:
                    to_proc.extend(st)

            def on_elem(x):
                if isinstance(x, int):
                    return "q_{" + str(x) + "}"
                return str(x)

            return "\\{" + ",".join(map(on_elem, elems)) + "\\}"

        fs.save_nfa_dot(B.shuffle(LA).shuffle(LB).shuffle(T),
                        "dev",
                        state_name=render_state_name)

        T_LEVEL1 = L("l1")
        T_LEVEL2 = L("l2")
        T_STANDBY1 = L("s1")
        T_STANDBY2 = L("s2")
        lbl_to_rex = {
            T_LEVEL1:
                Concat.from_list(map(Char, [B_P, B_R, LA_ON, T_S])),
            T_LEVEL2:
                Concat.from_list([
                    Char(B_P),
                    Char(B_R),
                    And(Char(T_C), Char(LB_ON)),
                    Char(T_S),
                ]),
            T_STANDBY1:
                concat(Char(T_T), Char(LA_OFF)),
            T_STANDBY2:
                concat(
                    Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                    And(Char(LB_OFF), Char(LA_OFF)),
                ),
        }

        TRIGGER = NFA(
            states=[0, 1, 2],
            alphabet=[T_LEVEL1, T_LEVEL2, T_STANDBY1, T_STANDBY2],
            transition_func=NFA.transition_edges([
                (0, [T_LEVEL1], 1),
                (1, [T_LEVEL2], 2),
                (1, [T_STANDBY1], 0),
                (2, [T_STANDBY2], 0),
            ]),
            start_state=0,
            accepted_states=lambda x: 0 <= x <= 2,
        )
        fs.save_nfa_dot(TRIGGER, "trigger-abs")
        trigger_r = nfa_to_regex(TRIGGER)

        print(trigger_r)

        # Replace tokens by REGEX
        trigger_r = replace(trigger_r, lbl_to_rex)
        ALL = (tuple(B.alphabet) + tuple(LA.alphabet) + tuple(LB.alphabet) +
               tuple(T.alphabet))

        trigger_nfa = regex_to_nfa(trigger_r, ALL)
        fs.save_nfa_dot(trigger_nfa, "trigger-full")
