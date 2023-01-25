import argparse
import sys

import yaml
import logging
from typing import List, Optional, Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("generate_makefile")

FULL_SYSTEM_SUFFIX = "extended"

MAKEFILE_TEMPLATE = """include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u $$USES_PATH$$
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS =$$PYTHON_OPTIMIZE$$

all: $$ALL_TARGET$$

pdf: $$MAIN_SYSTEM$$.pdf

png: $$MAIN_SYSTEM$$.png

scy: $$MAIN_SYSTEM$$.scy

USES = -u uses.yml

$$PYTHON_TARGETS$$

deps:
$$DEPS$$

$$MAIN_SYSTEM$$.scy: deps $$MAIN_SYSTEM$$.shy

$$EXAMPLE_FOLDER$$-stats.json:
$$STATS$$
stats: $$EXAMPLE_FOLDER$$-stats.json

clean:
	rm -f $$CLEAN_EXT$$
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
        "--uses",
        type=Path,
        default=None,
        help="Path to uses.yml",
    )
    parser.add_argument(
        "--optimize",
        help="Try to merge operations that share the same next operations in the Python code (BETA)",
        action="store_true",
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


def generate_makefile_content(
    example_path: Path, uses_path: Optional[Path] = None, optimize: bool = False
):
    python_files: List[Path] = _collect_py_files(example_path)
    logger.debug("Found python files: {0}".format(python_files))

    if python_files:
        scy_files: List[str] = _collect_scy_files(example_path, "py")
    else:
        scy_files: List[str] = _collect_scy_files(example_path, "shy")

    logger.debug("Found .scy files: {0}".format(scy_files))

    uses: Optional[Dict[str, str]] = _collect_uses(uses_path)
    logger.debug("Found uses: {0}".format(uses))

    if uses is not None:
        main_source_set = set(scy_files) - set(uses.values())
        if len(main_source_set) > 1:
            logger.warning(f"Found too many main files: {main_source_set}")
    else:
        uses = {}
        main_source_set = set(scy_files)

    try:
        main_source_filename = main_source_set.pop()
    except KeyError:
        msg = """Could not decide what is the main source!
        Found .shy files: {current_dir_sources}
        Uses: {uses}
                """.format(
            current_dir_sources=scy_files, uses=uses
        )
        logger.error(msg)
        sys.exit(255)

    logger.debug("Guessing main: {0}".format(main_source_filename))

    deps = ""
    clean_deps = ""
    stats = ""

    uses_parents: List[str] = []
    for use_path in uses.values():  # order of uses matters!
        use_basename = Path(use_path).stem  # basename without extension
        parent = Path(use_path).parent  # relative parent path
        if parent.name != Path(main_source_filename).parent.name:
            uses_parents.append(str(parent))
            deps += f"	$(MAKE) -C {parent} {use_basename}.scy\n"
            if python_files:
                deps += (
                    f"	$(MAKE) -C {parent} {use_basename}_{FULL_SYSTEM_SUFFIX}.scy\n"
                )
            clean_deps += f"	$(MAKE) -C {parent} clean\n"
            stats += f"	$(MAKE) -C {parent} {use_basename}-stats.json\n"
        else:
            deps += f"	$(MAKE) {use_basename}.scy\n"
            if python_files:
                deps += f"	$(MAKE) {use_basename}_{FULL_SYSTEM_SUFFIX}.scy\n"
            stats += f"	$(MAKE) {use_basename}-stats.json\n"

    if python_files:
        deps += f"	$(MAKE) {Path(main_source_filename).stem}_{FULL_SYSTEM_SUFFIX}.scy"
    else:
        deps = deps[:-1]  # remove extra newline

    stats += f"	$(MAKE) {Path(main_source_filename).stem}-stats.json\n"

    makefile_content: str = MAKEFILE_TEMPLATE

    makefile_content = makefile_content.replace("$$USES_PATH$$", uses_path.name)
    makefile_content = makefile_content.replace("$$DEPS$$", deps)
    makefile_content = makefile_content.replace("$$CLEAN_DEPS$$", clean_deps)
    makefile_content = makefile_content.replace("$$STATS$$", stats)

    makefile_content = makefile_content.replace(
        "$$MAIN_SYSTEM$$", Path(main_source_filename).stem
    )
    makefile_content = makefile_content.replace(
        "$$EXAMPLE_FOLDER$$", Path(example_path).absolute().name
    )

    default_clean_ext = "*.scy *.pdf *.png *.gv *-stats.json *.int *.smv"
    if not python_files:
        makefile_content = makefile_content.replace("$$ALL_TARGET$$", "scy")
        makefile_content = makefile_content.replace("$$PYTHON_TARGETS$$", "")
        makefile_content = makefile_content.replace("$$CLEAN_EXT$$", default_clean_ext)
        makefile_content = makefile_content.replace("$$PYTHON_OPTIMIZE$$", "")
    else:
        makefile_content = makefile_content.replace("$$ALL_TARGET$$", "py")
        makefile_content = makefile_content.replace(
            "$$PYTHON_TARGETS$$",
            f"py: {' '.join(_collect_shy_files(python_files))} scy",
        )
        default_clean_ext += " *.shy"
        makefile_content = makefile_content.replace("$$CLEAN_EXT$$", default_clean_ext)

        if optimize:
            makefile_content = makefile_content.replace(
                "$$PYTHON_OPTIMIZE$$", "--optimize"
            )
        else:
            makefile_content = makefile_content.replace("$$PYTHON_OPTIMIZE$$", "")

    # logger.debug(makefile_content)

    return makefile_content


def test_generate_makefile_content():
    generate_makefile_content(Path("./shelley-examples/aquamote_core_v4"))


def test_generate_makefile_content():
    generate_makefile_content(Path("./shelley-examples/paper_frankenstein_example"))


def _collect_py_files(example_path: Path):
    return [source for source in Path(example_path).glob("*.py")]


def _collect_shy_files(python_files: List[Path]):
    """
    Get a list of .shy filenames given a list of already collected python files
    """
    return [source.stem + ".shy" for source in python_files]


def _collect_scy_files(example_path: Path, target_ext: str = "scy"):
    """
    Get a list of .scy filenames by searching sources that have target_ext
    """
    return [
        source.stem + ".scy"
        for source in Path(example_path).glob("*.{0}".format(target_ext))
    ]


def _collect_uses(uses_path: Path) -> Optional[Dict[str, str]]:
    """
    Return example: {'Valve': 'valve.scy', 'Controller': 'controller.scy'}
    """
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


def run(example_path: str, uses_file_path: str, optimize: bool = False):
    makefile_content: str = generate_makefile_content(
        example_path, uses_file_path, optimize
    )
    makefile_path: Path = example_path / "Makefile"

    with makefile_path.open("w") as f:
        f.write(makefile_content)


def main() -> None:
    args: argparse.Namespace = create_parser().parse_args()

    # exclude_files_list: Optional[List[str]] = _collect_exclude(
    #     args.exclude, args.exclude_from_file
    # )

    if args.verbosity:
        logger.setLevel(logging.DEBUG)

    if args.input is None:
        example_path: Path = Path()  # add current folder
    else:
        example_path: Path = args.input

    if args.uses is None:
        uses_file_path: Path = example_path / "uses.yml"
    else:
        uses_file_path: Path = args.uses

    run(example_path, uses_file_path, args.optimize)


if __name__ == "__main__":
    main()
