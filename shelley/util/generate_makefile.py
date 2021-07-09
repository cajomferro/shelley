import traceback
import argparse
import yaml
import logging
from typing import List, Optional, Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("convert2lark")

MAKEFILE_TEMPLATE = """include ../common.mk
USES = -u $$USES_PATH$$

all: smv

pdf: $$MAIN_SYSTEM$$.pdf

png: $$MAIN_SYSTEM$$.png

smv: $$MAIN_SYSTEM$$.smv

scy: $$MAIN_SYSTEM$$.scy

USES = -u uses.yml

deps_smv:
$$DEPS_SMV$$
deps_scy:
$$DEPS_SCY$$
$$MAIN_SYSTEM$$.smv: deps_smv $$MAIN_SYSTEM$$.shy

$$MAIN_SYSTEM$$.scy: deps_scy $$MAIN_SYSTEM$$.shy

$$EXAMPLE_FOLDER$$-stats.json:
$$STATS$$
stats: $$EXAMPLE_FOLDER$$-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
$$CLEAN_DEPS$$

.PHONY: all pdf scy deps clean smv

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
    # parser.add_argument(
    #     "--exclude",
    #     type=List[str],
    #     nargs="*",
    #     default=None,
    #     help="List of exclude files",
    # )
    # parser.add_argument(
    #     "--exclude-from-file",
    #     type=Path,
    #     help="YAML file with filenames that should be excluded",
    #     default=None,
    # )

    return parser


def generate_config(
    example_path: Path,
    uses_path: Optional[Path] = None,
    # exclude_files: Optional[List[str]] = None,
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

    deps_smv = ""
    deps_scy = ""
    clean_deps = ""
    stats = ""

    uses_parents: List[str] = []
    for use_path in uses.values():  # order of uses matters!
        use_basename = Path(use_path).stem  # basename without extension
        parent = Path(use_path).parent  # relative parent path
        if parent.name != Path(main_source_filename).parent.name:
            uses_parents.append(str(parent))
            deps_smv += f"	$(MAKE) -C {parent} {use_basename}.smv\n"
            deps_scy += f"	$(MAKE) -C {parent} {use_basename}.scy\n"
            clean_deps += f"	$(MAKE) -C {parent} clean\n"
            stats += f"	$(MAKE) -C {parent} {use_basename}-stats.json\n"
        else:
            deps_smv += f"	$(MAKE) {use_basename}.smv\n"
            deps_scy += f"	$(MAKE) {use_basename}.scy\n"
            stats += f"	$(MAKE) {use_basename}-stats.json\n"

    stats += f"	$(MAKE) {Path(main_source_filename).stem}-stats.json\n"

    makefile_content: str = MAKEFILE_TEMPLATE

    makefile_content = makefile_content.replace("$$USES_PATH$$", uses_path.name)
    makefile_content = makefile_content.replace("$$DEPS_SMV$$", deps_smv)
    makefile_content = makefile_content.replace("$$DEPS_SCY$$", deps_scy)
    makefile_content = makefile_content.replace("$$CLEAN_DEPS$$", clean_deps)
    makefile_content = makefile_content.replace("$$STATS$$", stats)

    makefile_content = makefile_content.replace(
        "$$MAIN_SYSTEM$$", Path(main_source_filename).stem
    )
    makefile_content = makefile_content.replace(
        "$$EXAMPLE_FOLDER$$", Path(example_path).absolute().name
    )

    # print(makefile_content)

    return makefile_content


def test_generate_config():
    generate_config(Path("./shelley-examples/aquamote_core_v4"))


def test_generate_config_2():
    generate_config(Path("./shelley-examples/paper_frankenstein_example"))


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


def test__collect_uses(tmp_path):
    """
    uses.yml doesn't exist
    """
    uses: Optional[Dict[str, str]] = _collect_uses(tmp_path)
    assert uses is None


def test__collect_uses(tmp_path):
    """
    uses.yml exists but it is empty
    """
    USES_CONTENT = """
"""
    uses_path = tmp_path / "uses.yml"
    uses_path.write_text(USES_CONTENT)
    uses: Optional[Dict[str, str]] = _collect_uses(tmp_path)
    assert len(uses) == 0
    assert uses == {}


def test__collect_uses(tmp_path):
    """
    uses.yml exists and it contains 2 entries
    """
    USES_CONTENT = """
Valve: valve.scy
Timer: timer.scy
"""
    uses_path = tmp_path / "uses.yml"
    uses_path.write_text(USES_CONTENT)
    uses: Optional[Dict[str, str]] = _collect_uses(tmp_path)
    assert len(uses) == 2
    assert uses == {"Valve": "valve.scy", "Timer": "timer.scy"}


# def _collect_exclude(
#     exclude: Optional[List[str]] = None, exclude_from_file: Optional[Path] = None
# ) -> List[str]:
#     exclude_files_list: List[str] = []
#
#     if exclude:
#         exclude_files_list.extend(exclude)
#
#     if exclude_from_file:
#         with exclude_from_file.open("r") as f:
#             exclude_files_list.extend(yaml.safe_load(f))
#
#     return exclude_files_list
#
#
# def test__collect_exclude():
#     """
#     Do not exclude any file
#     """
#     exclude_files_list = _collect_exclude(None, None)
#     assert len(exclude_files_list) == 0
#
#
# def test__collect_exclude_2():
#     """
#     Exclude only from command line as a list of strings
#     """
#     exclude_files_list = _collect_exclude(["xx.shy", "yy.mk"], None)
#     assert len(exclude_files_list) == 2
#     assert exclude_files_list == ["xx.shy", "yy.mk"]
#
#
# def test__collect_exclude_3(tmp_path):
#     """
#     Exclude only from an external YAML file (which contains a list of strings)
#     """
#     exclude_content = """
#     - zz.shy
#     - kk.mk
#     """
#     exclude_yaml_path = tmp_path / "exclude.yml"
#     exclude_yaml_path.write_text(exclude_content)
#     exclude_files_list = _collect_exclude(None, exclude_yaml_path)
#     assert len(exclude_files_list) == 2
#     assert exclude_files_list == ["zz.shy", "kk.mk"]
#
#
# def test__collect_exclude_4(tmp_path):
#     """
#     Exclude both from the command line and the YAML file
#     """
#     exclude_content = """
#     - zz.shy
#     - kk.mk
#     """
#     exclude_yaml_path = tmp_path / "exclude.yml"
#     exclude_yaml_path.write_text(exclude_content)
#     exclude_files_list = _collect_exclude(["xx.shy", "yy.mk"], exclude_yaml_path)
#     assert len(exclude_files_list) == 4
#     assert exclude_files_list == ["xx.shy", "yy.mk", "zz.shy", "kk.mk"]


def run(example_path: str, uses_file_path: str):
    makefile_content: str = generate_config(example_path, uses_file_path)
    makefile_path: Path = example_path / "Makefile"

    with makefile_path.open("w") as f:
        f.write(makefile_content)


def main() -> None:
    args: argparse.Namespace = create_parser().parse_args()

    # exclude_files_list: Optional[List[str]] = _collect_exclude(
    #     args.exclude, args.exclude_from_file
    # )

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
