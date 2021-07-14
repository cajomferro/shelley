import yaml
import argparse
from typing import Optional, Any, Dict
from karakuri import regular
from pathlib import Path
import json
from dataclasses import dataclass, asdict


@dataclass
class Stats:
    nfa: Optional[int] = None
    int_nfa: Optional[int] = None
    int_nfa_no_sink: Optional[int] = None
    int_dfa: Optional[int] = None
    int_dfa_min_no_sink: Optional[int] = None


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
    parser.add_argument(
        "--int-nfa", action="store_true", help="Calculate integration NFA"
    )
    parser.add_argument(
        "--int-nfa-no-sink",
        action="store_true",
        help="Calculate integration NFA without sink states",
    )
    parser.add_argument(
        "--int-dfa", action="store_true", help="Calculate integration DFA"
    )
    parser.add_argument(
        "--int-dfa-min-no-sink",
        action="store_true",
        help="Calculate integration DFA minimized and without sink states",
    )

    return parser


def handle_fsm(
    n: regular.NFA[Any, str],
    stats: Stats,
    integration: bool = False,
    int_nfa: bool = True,
    int_nfa_no_sink: bool = True,
    int_dfa: bool = False,
    int_dfa_min_no_sink: bool = False,
) -> None:
    if not integration:
        stats.nfa = len(n)
    else:
        if int_nfa:
            stats.int_nfa = len(n)

        # Before minimizing, make sure we remove sink states, so that there
        # is a unique sink state when we convert to DFA; this is a quick
        # way of making the resulting DFA smaller
        if int_nfa_no_sink:
            n = n.remove_sink_states()
            stats.int_nfa_no_sink = len(n)

            if int_dfa:
                d: regular.DFA[Any, str] = regular.nfa_to_dfa(n)
                stats.int_dfa = len(d)

                if int_dfa_min_no_sink:
                    d = d.minimize()
                    stats.int_dfa_min_no_sink = len(d)


def main() -> None:
    parser = create_parser()
    args: argparse.Namespace = parser.parse_args()

    stats = Stats()

    path_scy = args.input[0]
    path_int = args.input[1]

    with path_scy.open(mode="r") as d:
        example_fsm: Dict = yaml.load(d, Loader=yaml.FullLoader)
        handle_fsm(regular.NFA.from_dict(example_fsm), stats, integration=False)

    if path_int.exists():
        with path_int.open(mode="r") as d:
            example_fsm: Dict = yaml.load(d, Loader=yaml.FullLoader)
            handle_fsm(
                regular.NFA.from_dict(example_fsm),
                stats,
                integration=True,
                int_nfa=args.int_nfa,
                int_nfa_no_sink=args.int_nfa_no_sink,
                int_dfa=args.int_dfa,
                int_dfa_min_no_sink=args.int_dfa_min_no_sink,
            )

    with args.output.open("w") as fp:
        json.dump([asdict(stats)], fp)

    # print("NFA:", out_device.nfa)
    # print("Integration NFA:", out_device.int_nfa)
    # print("Integration NFA no sinks:", out_device.int_nfa_no_sink)
    # print("Integration DFA:", out_device.int_dfa)
    # print("Integration Minimized DFA no sinks:", out_device.int_dfa_min_no_sink)


if __name__ == "__main__":
    main()
