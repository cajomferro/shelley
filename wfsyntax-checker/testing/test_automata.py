import sys
import os

from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import app
from automaton import *
from automaton.render_nfa import *
from regex import *
import regex


def replace(r, rules):
    if r is Nil:
        return r
    elif r is Empty:
        return r
    elif isinstance(r, Char):
        return rules.get(r.char, r)

    to_proc = [r]

    def do_subst(r, attr):
        child = getattr(r, attr)
        if isinstance(child, Char):
            new_child = rules.get(child.char, None)
            if new_child is not None and isinstance(new_child, str):
                raise ValueError(child.char)
            if new_child is not None:
                setattr(r, attr, new_child)
            return
        elif isinstance(child, Concat) or isinstance(
                child, Union) or isinstance(child, Star):
            to_proc.append(child)

    while len(to_proc) > 0:
        elem = to_proc.pop()
        if isinstance(elem, Star):
            do_subst(elem, "child")
        else:
            do_subst(elem, "left")
            do_subst(elem, "right")
    return r


def And(c1, c2):
    return Union(concat(c1, c2), concat(c2, c1))

def decode_triggers(triggers, decoder):
    """
    Given an NFA and a map of decoders, returns a REGEX with all the
    substitutions performed.
    """
    # Convert the given triggers into a regex
    triggers_r = nfa_to_regex(triggers)
    # Replace tokens by REGEX in decoder
    return replace(trigger_r, decoder)


def check_valid(devices, events, triggers):
    # Shuffle all devices:
    dev = devices.pop()
    for d in devices:
        dev = dev.shuffle(d)

    # Decode the triggers according to the decoder-map
    decoded_events_r = decode_triggers(events, triggers)
    # Get all tokens:
    alphabet = set()
    for d in devices:
        alphabet.update(d.alphabet)
    # Get the NFA
    decoded_events_n = regex_to_nfa(decoded_events, ALL)

    # TODO: We need to implement NFA subtraction
    # decoded_triggers -= dev
    # TODO: We need to implement the emptyness test
    # return decoded_triggers.is_empty()
    return False

def main(fs):
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


if __name__ == '__main__':
    os.chdir(str(Path(__file__).parent))
    with app.run() as fs:
        main(fs)
