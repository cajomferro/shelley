import yaml
import argparse
import sys
from typing import Union, Any
from karakuri import regular
from shelley.automata.view import fsm2dot, fsm2tex
from pathlib import Path
import json

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

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Visualize compiled files as state diagrams"
    )
    parser.add_argument(
        "input",
        type=argparse.FileType("r"),
        help="Path to the compiled yaml file (.scy or .scb)",
    )
    parser.add_argument("--dfa", action="store_true", help="Convert to a DFA first")
    parser.add_argument(
        "--no-epsilon", action="store_true", help="Remove epsilon transitions"
    )
    parser.add_argument(
        "--minimize-slow",
        action="store_true",
        help="Runs the naive DFA minimization algorithm",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="dot",
        help="Specify the output format (defaults to dot) pick 'tex' or any from https://www.graphviz.org/doc/info/output.html",
    )
    parser.add_argument("--no-sink", action="store_true", help="Remove sink states")
    parser.add_argument("--minimize", action="store_true", help="Minimize the DFA")
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        type=Path,
        default=None,
        help="Path to the generated DOT file (defaults to STDOUT)",
    )
    return parser


def handle_fsm(
    n: regular.NFA[Any, str], args: argparse.Namespace
) -> regular.NFA[Any, str]:
    if args.dfa:
        print("Input:", len(n), file=sys.stderr)
        # Convert the DFA back into an NFA to possibly remove sink states
        if args.minimize:
            # Before minimizing, make sure we remove sink states, so that there
            # is a unique sink state when we convert to DFA; this is a quick
            # way of making the resulting DFA smaller
            if not args.minimize_slow:
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

        if args.no_sink:
            n = n.remove_sink_states()
            print("NFA no sink:", len(n), file=sys.stderr)
        return n
    else:
        print("Input:", len(n))
        if args.no_epsilon:
            n = n.remove_epsilon_transitions()
            print("Remove epsilon:", len(n), file=sys.stderr)
        if args.no_sink:
            n = n.remove_sink_states()
            print("Remove sink states:", len(n), file=sys.stderr)
        return n


def main() -> None:
    parser = create_parser()
    args: argparse.Namespace = parser.parse_args()
    if args.minimize and not args.dfa:
        parser.error("The '--minimize' option requires '--dfa'")
    d = yaml.load(args.input, Loader=yaml.FullLoader)
    n: regular.NFA[Any, str] = handle_fsm(regular.NFA.from_dict(d), args)
    fp = sys.stdout if args.output is None else open(args.output, "w")
    if args.format == "json":
        json.dump(n.as_dict(flatten=True), fp)
        return
    if args.format == "yaml":
        yaml.dump(n.as_dict(flatten=True), fp)
        return
    if args.format == "fsm":
        if not args.no_epsilon and not args.dfa:
            parser.error("Option '--output fsm' requires either '--dfa' or '--no-epsilon'")
        fsm_dump(n.as_dict(flatten=True), fp)
        return


    if args.format == "tex":
        dot = fsm2tex(n)
    else:
        dot = fsm2dot(n)
    dot.format = "dot" if args.format == "tex" else args.format
    if dot.format == "dot":
        if args.output is None:
            print(dot, file=sys.stdout)
        else:
            with args.output.open("w") as fp:
                print(dot, file=fp)
    else:
        if args.output is None:
            sys.stdout.buffer.write(dot.pipe())
        else:
            with args.output.open("wb") as fp:
                fp.write(dot.pipe())
    #


if __name__ == "__main__":
    main()
