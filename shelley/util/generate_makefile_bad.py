import argparse
import yaml
from typing import List, Optional, Dict
from pathlib import Path

MAKEFILE_TEMPLATE = """include ../common.mk
USES = -u $$USES_PATH$$

all: scy

scy: $$MAIN_SYSTEM$$.scy

USES = -u uses.yml

deps_scy:
$$DEPS_SCY$$

$$MAIN_SYSTEM$$.scy: $$MAIN_SYSTEM$$.shy deps_scy
	! $(SHELLEYMC) $(USES) -s $< $(VALIDITY_CHECKS) $(DEBUG)

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
$$CLEAN_DEPS$$

.PHONY: all pdf scy deps clean

"""


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Creates a Makefile for one or more examples"
    )
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=None,
        help="Path to an example or a YAML file with several examples. If this is empty, assume current folder.",
    )
    parser.add_argument(
        "--uses", type=Path, default=None, help="Path to uses.yml",
    )

    return parser


def generate_config(
    example_path: Path, uses_path: Optional[Path] = None,
):

    current_dir_sources: List[str] = [
        source.stem + ".scy" for source in Path(example_path).glob("*.shy")
    ]
    uses: Optional[Dict[str, str]] = _collect_uses(uses_path)

    if uses is not None:
        main_source_set = set(current_dir_sources) - set(uses.values())
    else:
        uses = {}
        main_source_set = set(current_dir_sources)

    main_source_filename = main_source_set.pop()

    deps_scy = ""
    clean_deps = ""

    uses_parents: List[str] = []
    for use_path in uses.values():  # order of uses matters!
        use_basename = Path(use_path).stem  # basename without extension
        parent = Path(use_path).parent  # relative parent path
        if parent.name != Path(main_source_filename).parent.name:
            uses_parents.append(str(parent))
            deps_scy += f"	$(MAKE) -C {parent} {use_basename}.scy\n"
            clean_deps += f"	$(MAKE) -C {parent} clean\n"
        else:
            deps_scy += f"	$(MAKE) {use_basename}.scy\n"

    makefile_content: str = MAKEFILE_TEMPLATE

    makefile_content = makefile_content.replace("$$USES_PATH$$", uses_path.name)
    makefile_content = makefile_content.replace("$$DEPS_SCY$$", deps_scy)
    makefile_content = makefile_content.replace("$$CLEAN_DEPS$$", clean_deps)

    makefile_content = makefile_content.replace(
        "$$MAIN_SYSTEM$$", Path(main_source_filename).stem
    )
    makefile_content = makefile_content.replace(
        "$$EXAMPLE_FOLDER$$", Path(example_path).absolute().name
    )

    return makefile_content


def _collect_uses(uses_path: Path) -> Optional[Dict[str, str]]:
    uses: Optional[Dict[str, str]] = None
    if uses_path.exists():
        with uses_path.open("r") as f:
            uses = yaml.safe_load(f)
    else:
        print(
            "WARNING! uses.yml not found! I am creating an empty one. For a different uses path, append --uses USES_PATH"
        )
        uses_path.touch()

    return uses


def run(example_path: str, uses_file_path: str):
    makefile_content: str = generate_config(example_path, uses_file_path)
    makefile_path: Path = example_path / "Makefile"

    with makefile_path.open("w") as f:
        f.write(makefile_content)


def main() -> None:
    args: argparse.Namespace = create_parser().parse_args()

    if args.input is None:
        example_path: Path = Path()  # add current folder
    else:
        example_path: Path = args.input

    if args.uses is None:
        uses_file_path: Path = example_path / "uses.yml"
    else:
        uses_file_path: Path = args.uses

    run(example_path, uses_file_path)


if __name__ == "__main__":
    main()
