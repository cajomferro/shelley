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
    integration: Path, smv_path: Path, filter: str = None
) -> None:
    fsm_dict = load_integration(integration)

    n: regular.NFA[Any, str] = handle_fsm(
        regular.NFA.from_dict(fsm_dict), dfa=True, filter=filter
    )

    with smv_path.open("w") as fp:
        smv_dump(state_diagram=n.as_dict(flatten=True), fp=fp)


# LTLSPEC (action=level1) -> (action=standby1 | action=level1);
def smv_dump(
    state_diagram, fp, var_action="_action", var_eos="_eos", var_state="_state"
) -> None:

    to_act = lambda x: x if x is None else x.replace(".", "_")
    INDENT = "    "

    def render_values(elem):
        if isinstance(elem, str):
            return elem
        if len(elem) == 0:
            raise ValueError()
        return "{" + ", ".join(map(str, elem)) + "}"

    def decl_var(name, values):
        print(f"{INDENT}{name}: {render_values(values)};", file=fp)

    def add_edge(src, char, dst):
        char = to_act(char)
        act = f" & {var_action}={char}" if char is not None else ""
        print(f"{var_state}={src}{act}: {dst};", file=fp)

    def init_var(name, values):
        print(f"{INDENT}init({name}) := {render_values(values)};", file=fp)

    def next_var_case(variable, elems):
        print(f"{INDENT}next({variable}) := case", file=fp)
        for (cond, res) in elems:
            res = render_values(res)
            print(f"{INDENT}{INDENT}{cond} : {res};", file=fp)
        print(f"{INDENT}esac;", file=fp)

    acts = list(
        set(
            to_act(edge["char"])
            for edge in state_diagram["edges"]
            if edge["char"] is not None
        )
    )
    acts.sort()
    print("MODULE main", file=fp)
    print("VAR", file=fp)
    decl_var(f"{var_eos}", "boolean")
    decl_var(f"{var_action}", acts)

    states = list(
        set(x["src"] for x in state_diagram["edges"]).union(
            set(x["src"] for x in state_diagram["edges"])
        )
    )
    states.sort()
    decl_var(f"{var_state}", states)
    print("ASSIGN", file=fp)

    # State
    init_var(f"{var_state}", [state_diagram["start_state"]])
    print(f"{INDENT}next({var_state}) := case", file=fp)
    print(
        f"{INDENT}{INDENT}{var_eos}: {var_state}; -- finished, no change in state",
        file=fp,
    )
    for edge in state_diagram["edges"]:
        print(f"{INDENT}{INDENT}", end="", file=fp)
        src, char, dst = edge["src"], edge["char"], edge["dst"]
        add_edge(src, char, dst)
    print(f"{INDENT}esac;", file=fp)
    # Action
    if len(acts) > 1:
        init_var(f"{var_action}", acts)
        next_var_case(var_action, [(var_eos, var_action), ("TRUE", acts)])

    # EOS
    init_var(
        var_eos,
        ["TRUE", "FALSE"]
        if state_diagram["start_state"] in state_diagram["accepted_states"]
        else ["FALSE"],
    )
    lines = [
        (var_eos, "TRUE"),
    ]
    for edge in state_diagram["edges"]:
        src, char, dst = edge["src"], edge["char"], edge["dst"]
        if dst in state_diagram["accepted_states"]:
            char = to_act(char)
            act = f" & {var_action}={char}" if char is not None else ""
            lines.append((f"{var_state}={src}{act}", ["TRUE", "FALSE"]))
    lines.append(("TRUE", "FALSE"))
    next_var_case(var_eos, lines)
    print(f"FAIRNESS {var_eos};", file=fp)

    print(f"LTLSPEC F ({var_eos}); -- sanity check", file=fp)
    print(
        f"LTLSPEC G ({var_eos} -> G({var_eos}) & X({var_eos})); -- sanity check",
        file=fp,
    )


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
