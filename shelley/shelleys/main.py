import yaml
import argparse
import sys, os
from typing import Union, Any, Dict
from karakuri import regular
from shelley.automata.view import fsm2dot, fsm2tex
from pathlib import Path
import json
from dataclasses import dataclass, asdict


@dataclass
class OutDevice:
    nfa: int = 0
    int_nfa: int = 0
    int_nfa_no_sink: int = 0
    int_dfa: int = 0
    int_dfa_min_no_sink: int = 0


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Visualize compiled files as state diagrams"
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs=2,
        help="Path to the compiled yaml file (.scy or .scb) and compiled integration yaml file (.int)",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=Path,
        help="Path to the generated JSON file",
    )
    return parser


def handle_fsm(n: regular.NFA[Any, str], out_device: OutDevice, integration: bool = False) -> None:
    # Before minimizing, make sure we remove sink states, so that there
    # is a unique sink state when we convert to DFA; this is a quick
    # way of making the resulting DFA smaller

    if not integration:
        out_device.nfa = len(n)
    else:
        out_device.int_nfa = len(n)

        n = n.remove_sink_states()
        out_device.int_nfa_no_sink = len(n)

        d: regular.DFA[Any, str] = regular.nfa_to_dfa(n)
        out_device.int_dfa = len(d)

        d = d.minimize()
        out_device.int_dfa_min_no_sink = len(d)


def main() -> None:
    parser = create_parser()
    args: argparse.Namespace = parser.parse_args()

    out_device = OutDevice()

    path_scy = args.input[0]
    path_int = args.input[1]

    with path_scy.open(mode="r") as d:
        example_fsm: Dict = yaml.load(d, Loader=yaml.FullLoader)
        handle_fsm(regular.NFA.from_dict(example_fsm), out_device, integration=False)

    if path_int.exists():
        with path_int.open(mode="r") as d:
            example_fsm: Dict = yaml.load(d, Loader=yaml.FullLoader)
            handle_fsm(regular.NFA.from_dict(example_fsm), out_device, integration=True)

    with args.output.open("w") as fp:
        json.dump(asdict(out_device), fp)

    # print("NFA:", out_device.nfa)
    # print("Integration NFA:", out_device.int_nfa)
    # print("Integration NFA no sinks:", out_device.int_nfa_no_sink)
    # print("Integration DFA:", out_device.int_dfa)
    # print("Integration Minimized DFA no sinks:", out_device.int_dfa_min_no_sink)


if __name__ == "__main__":
    main()
