import yaml
import argparse
import sys

from shelley.automata.view import automaton2dot, dfa2tex


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Visualize compiled files as state diagrams"
    )
    parser.add_argument("input",
        type=argparse.FileType('r'),
        help="Path to the compiled yaml file (.scy or .scb)"
    )
    parser.add_argument("--tex", action="store_true", help="Generate dot2tex")
    parser.add_argument("-o", "--output",
        nargs='?',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help="Path to the generated DOT file (defaults to STDOUT)"
    )
    return parser


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()


def main() -> None:
    args: argparse.Namespace = get_args()
    d = yaml.load(args.input, Loader=yaml.FullLoader)
    if args.tex:
        dot = dfa2tex(d)
    else:
        dot = automaton2dot(d)
    print(dot, file=args.output)


if __name__ == "__main__":
    main()
