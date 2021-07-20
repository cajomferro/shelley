import re
from typing import Any, Optional
from karakuri import regular
from pathlib import Path
import yaml
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleyv")


def fsm2smv(
    fsm_model: Path,
    smv_model: Path,
    project_prefix: Optional[str] = None,
    ctl_compatible: bool = False,
) -> None:
    """
    Convert an FSM model (.scy) to an SMV model (.smv).
    @param fsm_model: path to the input .scy file
    @param smv_model: path to the output .smv file
    @param filter_instance:
    """

    with fsm_model.open("r") as fp:
        fsm_dict = yaml.load(fp, Loader=yaml.FullLoader)

    d: regular.DFA[Any, str] = handle_fsm(
        regular.NFA.from_dict(fsm_dict),
        dfa=True,
        project_prefix=project_prefix,
    ).result_dfa
    # Make sure that there is no empty string
    d = d.subtract(regular.DFA.make_nil(d.alphabet))
    n = regular.dfa_to_nfa(d)

    with smv_model.open("w") as fp:
        smv_dump(
            state_diagram=n.as_dict(flatten=True),
            fp=fp,
            ctl_compatible=ctl_compatible
        )


# LTLSPEC (action=level1) -> (action=standby1 | action=level1);
def smv_dump(
    state_diagram,
    fp,
    var_action: str = "_action",
    var_eos: str = "_eos",
    var_state: str = "_state",
    ctl_action_init: str = "_ainit",
    ctl_first_state: int = -1,
    ctl_compatible: bool = False,
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

    if ctl_compatible is True:
        decl_var(f"{var_action}", [ctl_action_init] + acts)
    else:
        decl_var(f"{var_action}", acts)

    states = list(
        set(x["src"] for x in state_diagram["edges"]).union(
            set(x["src"] for x in state_diagram["edges"])
        )
    )
    states.sort()

    if ctl_compatible is True:
        decl_var(f"{var_state}", [ctl_first_state] + states)
    else:
        decl_var(f"{var_state}", states)

    print("ASSIGN", file=fp)

    # State
    if ctl_compatible is True:
        init_var(f"{var_state}", [ctl_first_state])
    else:
        init_var(f"{var_state}", [state_diagram["start_state"]])

    print(f"{INDENT}next({var_state}) := case", file=fp)
    print(
        f"{INDENT}{INDENT}{var_eos}: {var_state}; -- finished, no change in state",
        file=fp,
    )

    if ctl_compatible is True:

        # dummy first state (needed for CTL)
        print(
            f"{INDENT}{INDENT}{var_state}={ctl_first_state}: {state_diagram['start_state']}; -- FSM initial state",
            file=fp,
        )

        # dummy init action (needed for CTL)
        print(
            f"{INDENT}{INDENT}{var_action}={ctl_action_init}: {var_state}; -- never executed",
            file=fp,
        )

    for edge in state_diagram["edges"]:
        print(f"{INDENT}{INDENT}", end="", file=fp)
        src, char, dst = edge["src"], edge["char"], edge["dst"]
        add_edge(src, char, dst)
    print(f"{INDENT}esac;", file=fp)

    # Action
    if len(acts) > 1:
        if ctl_compatible is True:
            init_var(f"{var_action}", {ctl_action_init})
        else:
            init_var(f"{var_action}", acts)

        next_var_case(
            var_action, [(var_eos, var_action), ("TRUE", acts),],
        )

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

    print(f"\nFAIRNESS {var_eos};", file=fp)


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


@dataclass
class FSMStats:
    input: Optional[str] = None
    dfa_no_sinks: Optional[str] = None
    dfa: Optional[str] = None
    dfa_min: Optional[str] = None
    dfa_to_nfa_no_sink: Optional[str] = None
    nfa_no_epsilon: Optional[str] = None
    nfa_no_sinks: Optional[str] = None
    result_dfa: Optional[regular.DFA[Any, str]] = None
    result: Optional[regular.NFA[Any, str]] = None

    def __str__(self):
        text = ""
        if self.input is not None:
            text += f"Input: {self.input}\n"
        if self.dfa is not None:
            text += f"DFA: {self.dfa}\n"
        if self.dfa_no_sinks is not None:
            text += f"DFA no sinks: {self.dfa_no_sinks}\n"
        if self.dfa_min is not None:
            text += f"DFA minimized: {self.dfa_min}\n"
        if self.dfa_to_nfa_no_sink is not None:
            text += f"DFA2NFA no sinks: {self.dfa_to_nfa_no_sink}\n"
        if self.nfa_no_epsilon is not None:
            text += f"NFA no epsilon: {self.nfa_no_epsilon}\n"
        if self.nfa_no_sinks is not None:
            text += f"NFA no sinks: {self.nfa_no_sinks}\n"
        return text.strip()


def handle_fsm(
    n: regular.NFA[Any, str],
    filter: str = None,
    dfa: bool = False,
    minimize: bool = False,
    minimize_slow: bool = False,
    no_sink: bool = False,
    no_epsilon: bool = False,
    project_prefix: Optional[str] = None,
) -> FSMStats:
    fsm_stats = FSMStats()

    if project_prefix is not None:
        translate = dict()
        translate[None] = None
        offset = len(project_prefix)
        for name in n.alphabet:
            if name is not None and name.startswith(project_prefix):
                translate[name] = name[offset:]
            else:
                # Skip otherwise
                translate[name] = None
        n = n.map_alphabet(translate)

    if filter is not None:
        pattern = re.compile(filter)

        def on_elem(x):
            return x if x is None else pattern.match(x)

        n = n.filter_char(on_elem)

    fsm_stats.input = len(n)

    if dfa:
        # logger.debug(f"Input: {len(n)}")

        # Convert the DFA back into an NFA to possibly remove sink states
        if minimize:
            # Before minimizing, make sure we remove sink states, so that there
            # is a unique sink state when we convert to DFA; this is a quick
            # way of making the resulting DFA smaller
            if not minimize_slow:
                n = n.remove_sink_states()
                # logger.debug("No sinks:", len(n), file=sys.stderr)
                fsm_stats.dfa_no_sinks = len(n)
            d: regular.DFA[Any, str] = regular.nfa_to_dfa(n)
            # print("DFA:", len(d), file=sys.stderr)
            fsm_stats.dfa = len(d)
            d = d.minimize()
            # print("Minimized DFA:", len(d), file=sys.stderr)
            fsm_stats.dfa_min = len(d)
        else:
            d = regular.nfa_to_dfa(n).flatten()
            # print("DFA:", len(d), file=sys.stderr)
            fsm_stats.dfa = len(d)
        fsm_stats.result_dfa = d
        n = regular.dfa_to_nfa(d)

        if no_sink:
            n = n.remove_sink_states()
            # print("NFA no sink:", len(n), file=sys.stderr)
            fsm_stats.dfa_to_nfa_no_sink = len(n)

        fsm_stats.result = n

    else:
        # print("Input:", len(n))
        if no_epsilon:
            n = n.remove_epsilon_transitions()
            # print("Remove epsilon:", len(n), file=sys.stderr)
            fsm_stats.nfa_no_epsilon = len(n)
        if no_sink:
            n = n.remove_sink_states()
            # print("Remove sink states:", len(n), file=sys.stderr)
            fsm_stats.nfa_no_sinks = len(n)

        fsm_stats.result = n

    return fsm_stats
