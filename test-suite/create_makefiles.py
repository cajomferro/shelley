import os
import traceback
import argparse
import yaml
from typing import List
from pathlib import Path
from shelley.util import generate_makefile
from shelley.util import generate_makefile_bad


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate yaml with list of examples")
    parser.add_argument(
        "-x",
        "--exclude-files",
        type=Path,
        help="YAML file with filenames that should be excluded",
        default=None,
    )

    return parser


def run(examples_path: Path, exclude_files: List[str], output_path: Path):

    errors: int = 0
    for foldername in sorted(os.listdir(examples_path)):
        example_path = Path(examples_path, foldername).absolute()
        if (
            not example_path.is_file()
            and not foldername in exclude_files
            and not foldername.startswith("_")
        ):
            print(f"Processing {foldername}")
            try:
                if not foldername.startswith("bad"):
                    generate_makefile.run(example_path, example_path / "uses.yml")
                else:
                    generate_makefile_bad.run(example_path, example_path / "uses.yml")
            except:
                errors += 1
                traceback.print_exc()

    print(f"Done! Errors: {errors}")


def main() -> None:
    args: argparse.Namespace = create_parser().parse_args()

    exclude_files = []
    if args.exclude_files:
        with args.exclude_files.open("r") as f:
            exclude_files = yaml.safe_load(f)

    output_path = Path("examples.mk")
    examples_path = Path(".")

    run(examples_path, exclude_files, output_path)


if __name__ == "__main__":
    main()
