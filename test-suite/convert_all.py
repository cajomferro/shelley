import os
import argparse
import yaml
from typing import List
from pathlib import Path
from convert2lark import convert as convert2lark


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate yaml with list of examples")
    parser.add_argument(
        "--exclude-files",
        type=Path,
        help="YAML file with filenames that should be excluded",
        default=None,
    )

    return parser


def list_examples(examples_path: Path, exclude_files: List[str]):
    for foldername in sorted(os.listdir(examples_path)):
        example_path = Path(examples_path, foldername).absolute()
        if not os.path.isfile(example_path) and not foldername in exclude_files:
            convert2lark(example_path, ["uses.yml", "Makefile"])


def main() -> None:
    args: argparse.Namespace = create_parser().parse_args()

    exclude_files = []
    if args.exclude_files:
        with args.exclude_files.open("r") as f:
            exclude_files = yaml.safe_load(f)

    examples_path = Path(".")

    list_examples(examples_path, exclude_files)


if __name__ == "__main__":
    main()
