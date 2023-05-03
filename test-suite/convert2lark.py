import os
import argparse
import yaml
import logging
from typing import List
from pathlib import Path
from natsort import natsorted
from shelley.parsers.yaml import yaml2lark

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("convert2lark")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate yaml with list of examples")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "--examples-path", type=Path, help="Examples base path", required=True,
    )
    parser.add_argument(
        "--exclude", type=str, nargs="*", default=[], help="List of exclude files"
    )
    parser.add_argument(
        "--exclude-files",
        type=Path,
        help="YAML file with filenames that should be excluded",
        default=None,
    )

    return parser


def convert(examples_path: Path, exclude_files: List[str]):
    print(exclude_files)

    all_files = natsorted(os.listdir(examples_path), key=lambda y: y.lower())

    for filename in all_files:
        if filename.endswith(".yml") and not filename in exclude_files:
            logger.debug(filename)
            yaml_path = Path(examples_path, filename).absolute()
            lark_path = Path(str(yaml_path)[:-4] + ".shy")
            print(lark_path)
            yaml2lark.translate(yaml_path, lark_path)


def main() -> None:
    args: argparse.Namespace = create_parser().parse_args()

    exclude_files = []
    if args.exclude_files:
        with args.exclude_files.open("r") as f:
            exclude_files = yaml.safe_load(f)

    convert(args.examples_path, args.exclude, exclude_files)


if __name__ == "__main__":
    main()
