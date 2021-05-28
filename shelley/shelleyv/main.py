import yaml
import argparse
import sys
from typing import Any
from karakuri import regular
from pathlib import Path
import json
import logging

from shelley.automata.view import fsm2dot, fsm2tex
from shelley.shelleyv import shelleyv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleyv")
VERBOSE: bool = False


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Visualize compiled files as state diagrams"
    )
    parser.add_argument(
        "input", type=Path, help="Path to the compiled yaml file (.scy or .scb)",
    )
    parser.add_argument(
        "--dfa", default=False, action="store_true", help="Convert to a DFA first"
    )
    parser.add_argument(
        "--no-epsilon",
        default=False,
        action="store_true",
        help="Remove epsilon transitions",
    )
    parser.add_argument(
        "--minimize-slow",
        default=False,
        action="store_true",
        help="Runs the naive DFA minimization algorithm",
    )
    parser.add_argument(
        "--format",
        "-f",
        default="dot",
        help="Specify the output format (defaults to dot) pick 'tex' or any from https://www.graphviz.org/doc/info/output.html",
    )
    parser.add_argument(
        "--filter",
        default=None,
        help="Keep only the (operations/calls) that match the given regex, hide (epsilon) the remaining ones.",
    )
    parser.add_argument(
        "--no-sink", default=False, action="store_true", help="Remove sink states"
    )
    parser.add_argument(
        "--minimize", default=False, action="store_true", help="Minimize the DFA"
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        type=Path,
        default=None,
        help="Path to the generated DOT file (defaults to STDOUT)",
    )
    return parser


def main() -> None:
    parser = create_parser()
    args: argparse.Namespace = parser.parse_args()
    if args.minimize and not args.dfa:
        parser.error("The '--minimize' option requires '--dfa'")

    with args.input.open() as fp:
        d = yaml.load(fp, Loader=yaml.FullLoader)

    fsm_stats: shelleyv.FSMStats = shelleyv.handle_fsm(
        regular.NFA.from_dict(d),
        args.filter,
        args.dfa,
        args.minimize,
        args.minimize_slow,
        args.no_sink,
        args.no_epsilon,
    )

    n: regular.NFA[Any, str] = fsm_stats.result

    print(str(fsm_stats))

    fp = sys.stdout if args.output is None else open(args.output, "w")

    if args.format == "json":
        json.dump(n.as_dict(flatten=True), fp)
        return
    if args.format == "yaml":
        yaml.dump(n.as_dict(flatten=True), fp)
        return
    if args.format == "fsm":
        if not args.no_epsilon and not args.dfa:
            parser.error(
                "Option '--output fsm' requires either '--dfa' or '--no-epsilon'"
            )
        shelleyv.fsm_dump(n.as_dict(flatten=True), fp)
        return
    if args.format == "mclr2":
        shelleyv.mclr2_dump(n.as_dict(flatten=True), fp)
        return
    if args.format == "smv":
        if not args.dfa:
            parser.error("Option '--output smv' requires '--dfa'")
        shelleyv.smv_dump(state_diagram=n.as_dict(flatten=True), fp=fp)
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
