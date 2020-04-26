import yaml
import os
import argparse

from shelley.automata.view import automaton2dot


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Vizualize compiled files as state diagrams')
    parser.add_argument("input", help="Path to the compiled yaml file (.scy or .scb)")
    parser.add_argument("-o", "--output", help="Path to the generated dot file")
    return parser


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()


def main(args: argparse.Namespace) -> None:
    with open(args.input, 'r') as f:
        d = yaml.load(f, Loader=yaml.FullLoader)

    dot = automaton2dot(d)

    with open(args.output, 'w') as fp:
        print(dot, file=fp)


if __name__ == "__main__":
    main(get_args())
