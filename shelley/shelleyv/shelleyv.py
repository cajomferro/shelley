import sys
import re
from typing import Any
from karakuri import regular
from pathlib import Path
import yaml
from typing import Dict
from shelley.shelleymc import ltlf
from io import StringIO


def load_integration(integration_path: Path) -> Dict:
    with integration_path.open() as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)


def create_smv_from_integration_model(
    integration: Path, filter: str = None
) -> StringIO:
    fsm_dict = load_integration(integration)

    n: regular.NFA[Any, str] = handle_fsm(
        regular.NFA.from_dict(fsm_dict), dfa=True, filter=filter
    )

    smv_model: StringIO = ltlf.generate_smv(state_diagram=n.as_dict(flatten=True))

    return smv_model


def mclr2_dump(state_diagram, fp):
    to_state = lambda x: "Q_" + str(x)
    to_act = lambda x: x if x is None else x.replace(".", "_")
    to_edge = lambda act, dst: act + "." + dst if act is not None else dst
    acts = list(
        set(
            to_act(edge["char"])
            for edge in state_diagram["edges"]
            if edge["char"] is not None
        )
    )
    acts.sort()
    if len(acts) > 0:
        print("act", ", ".join(acts), ";", file=fp)
    # Build src -> list [(char, dst)]
    procs = dict()
    for edge in state_diagram["edges"]:
        src = to_state(edge["src"])
        dst = to_state(edge["dst"])
        char = to_act(edge["char"])
        some = procs.get(src, None)
        if some is None:
            procs[src] = some = (edge["src"] in state_diagram["accepted_states"], [])
        _, target = some
        target.append((char, dst))
    # Build the procs:
    if len(procs) > 0:
        print("proc", file=fp)
        for (src, (accepted, targets)) in procs.items():
            targets = [to_edge(act, dst) for (act, dst) in targets]
            if accepted:
                targets.append("delta")
            print("\t", src, "=", " + ".join(targets), file=fp)
    print("init", to_state(state_diagram["start_state"]), ";", file=fp)


def fsm_dump(state_diagram, fp):
    start = state_diagram["start_state"]
    state_to_int = {start: 1}
    int_to_state = [start]
    curr_state = 1
    # Build bijection between states and integers
    for edge in state_diagram["edges"]:
        for st in (edge["src"], edge["dst"]):
            st_idx = state_to_int.get(st, None)
            if st_idx is None:
                st_idx = curr_state
                curr_state += 1
                state_to_int[st] = st_idx
                int_to_state.append(st)
    assert len(state_to_int) == len(int_to_state)
    cardinal = len(state_to_int)
    states = " ".join('"{}"'.format(x) for x in range(cardinal))
    print(f"q({cardinal})", "State", states, file=fp)
    print("---", file=fp)
    for st in range(cardinal):
        print(st, file=fp)
    print("---", file=fp)
    for edge in state_diagram["edges"]:
        src = state_to_int[edge["src"]]
        dst = state_to_int[edge["dst"]]
        char = '"' + edge["char"] + '"'
        print(src, dst, char, file=fp)


def handle_fsm(
    n: regular.NFA[Any, str],
    filter: str = None,
    dfa: bool = False,
    minimize: bool = False,
    minimize_slow: bool = False,
    no_sink: bool = False,
    no_epsilon: bool = False,
) -> regular.NFA[Any, str]:
    if filter is not None:
        pattern = re.compile(filter)

        def on_elem(x):
            return x if x is None else pattern.match(x)

        n = n.filter_char(on_elem)
    if dfa:
        print("Input:", len(n), file=sys.stderr)
        # Convert the DFA back into an NFA to possibly remove sink states
        if minimize:
            # Before minimizing, make sure we remove sink states, so that there
            # is a unique sink state when we convert to DFA; this is a quick
            # way of making the resulting DFA smaller
            if not minimize_slow:
                n = n.remove_sink_states()
                print("No sinks:", len(n), file=sys.stderr)
            d: regular.DFA[Any, str] = regular.nfa_to_dfa(n)
            print("DFA:", len(d), file=sys.stderr)
            d = d.minimize()
            print("Minimized DFA:", len(d), file=sys.stderr)
        else:
            d = regular.nfa_to_dfa(n).flatten()
            print("DFA:", len(d), file=sys.stderr)

        n = regular.dfa_to_nfa(d)

        if no_sink:
            n = n.remove_sink_states()
            print("NFA no sink:", len(n), file=sys.stderr)
        return n
    else:
        print("Input:", len(n))
        if no_epsilon:
            n = n.remove_epsilon_transitions()
            print("Remove epsilon:", len(n), file=sys.stderr)
        if no_sink:
            n = n.remove_sink_states()
            print("Remove sink states:", len(n), file=sys.stderr)
        return n
