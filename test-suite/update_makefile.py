import os
import argparse
import yaml
from typing import List
from pathlib import Path


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


def list_examples(examples_path: Path, exclude_files: List[str], output_path: Path):
    template = """bad:
	$$BAD_DIRECT$$

good:
	$$SCY$$

clean:
	$(MAKE) -C base clean
	$$CLEAN$$
"""

    list_run = ""
    list_clean = ""
    list_bad_scy = ""

    for foldername in sorted(os.listdir(examples_path)):
        example_path = Path(examples_path, foldername).absolute()
        if (
            not os.path.isfile(example_path)
            and not foldername in exclude_files
            and not foldername.startswith("_")
        ):  # and not foldername.startswith("bad"):
            list_clean += f"$(MAKE) -C {foldername} clean\n	"
            if foldername.startswith("bad"):
                # if not foldername.startswith("bad_ambiguity"):
                #     list_bad_smv += f"$(MAKE) -C {foldername} smv\n	"
                list_bad_scy += f"$(MAKE) -C {foldername} scy\n	"
            else:
                list_run += f"$(MAKE) -C {foldername} scy\n	"

    list_run = list_run[:-2]
    list_clean = list_clean[:-2]
    list_bad_scy = list_bad_scy[:-2]

    template = template.replace("$$SCY$$", list_run)
    template = template.replace("$$CLEAN$$", list_clean)
    template = template.replace("$$BAD_DIRECT$$", list_bad_scy)
    template.strip()

    with Path(output_path).open(mode="w") as f:
        f.write(template)


def main() -> None:
    args: argparse.Namespace = create_parser().parse_args()

    exclude_files = []
    if args.exclude_files:
        with args.exclude_files.open("r") as f:
            exclude_files = yaml.safe_load(f)

    output_path = Path("examples.mk")
    examples_path = Path(".")

    list_examples(examples_path, exclude_files, output_path)


if __name__ == "__main__":
    main()
