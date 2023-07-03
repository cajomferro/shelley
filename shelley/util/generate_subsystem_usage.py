import argparse
from pathlib import Path
from shelley.shelleyv.main import main as shelleyv_main


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate subsystem usage")

    parser.add_argument(
        "input",
        type=Path,
        help="Path to the compiled file (.scy or .scb)",
    )

    parser.add_argument(
        "subsystem_name",
        type=str,
        help="Work with operations from a specific subsystem only",
    )

    parser.add_argument(
        "--format",
        "-f",
        default="png",
        help="Specify the output format (defaults to dot) pick 'tex' or any from https://www.graphviz.org/doc/info/output.html",
    )

    return parser


def main() -> None:
    parser = create_parser()
    args: argparse.Namespace = parser.parse_args()
    shelleyv_main(
        [
            "--dfa",
            "--dfa-no-empty-string",
            "--nfa-no-sink",
            "--dfa-no-sink",
            f"--subsystem_name={args.subsystem_name}.",
            f"--format={args.format}",
            f"{args.input}-i.scy",
            f"-o={args.input}-d-{args.subsystem_name}.{args.format}",
        ]
    )


if __name__ == "__main__":
    main()
