from typing import Dict, Optional
from pathlib import Path
import logging
import argparse
import sys

from shelleypy.checker import settings
from shelleypy.checker.exceptions import CompilationError
from shelleypy.checker.checker import check

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyshelley")


def get_command_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile shelley files")
    parser.add_argument("input", nargs=1, type=Path,
                        help="Path to the input system (Python file)")
    parser.add_argument("-u", "--uses", type=Path, required=True,
                        help="path to the Shelley spec (YAML)")
    parser.add_argument("-o", "--output", type=Path, help="path to store shelley file")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    return parser.parse_args()


# def parse_uses(uses_path: Optional[Path]) -> Dict[str, str]:
#     if uses_path is None:
#         return {}
#
#     uses: Dict[str, str]
#     with uses_path.open(mode="r") as f:
#         uses = yaml.safe_load(f)
#
#     if uses is None:
#         return {}  # empty or commented yaml
#     elif isinstance(uses, dict):
#         return uses
#     else:
#         raise CompilationError(
#             "Shelley parser error: uses file must be a valid dictionary"
#         )


def main() -> None:
    args: argparse.Namespace = get_command_args()

    settings.VERBOSE = args.verbosity
    if settings.VERBOSE:
        logger.setLevel(logging.DEBUG)

    input_path: Path = args.input[0]
    logger.debug("Input python file: {0}".format(Path.absolute(input_path)))
    logger.debug("Input uses file: {0}".format(Path.absolute(args.uses)))

    try:
        check(
            src_path=input_path,
            # uses=parse_uses(args.uses),
            uses_path=args.uses,
            output_path=args.output,
        )
        logger.debug("OK!")
    except CompilationError as error:
        if settings.VERBOSE:
            logger.error(str(error), exc_info=settings.VERBOSE)
        else:
            print(str(error), file=sys.stderr)
        logger.debug("ERROR!")
        sys.exit(1)


if __name__ == "__main__":
    main()
