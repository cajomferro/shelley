from typing import Dict, Optional
from pathlib import Path
import logging
import argparse
import sys
import yaml

from shelley.shelleyc import settings
from shelley.shelleyc.exceptions import CompilationError
from shelley.shelleyc import compile_shelley

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleyc")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile shelley files")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    parser.add_argument("-u", "--uses", type=Path, help="path to file with uses")
    parser.add_argument("-o", "--output", type=Path, help="path to store compile file")
    parser.add_argument(
        "-b", "--binary", help="generate binary files", action="store_true"
    )
    parser.add_argument(
        "-d",
        "--device",
        type=Path,
        help="Path to the input example yaml file",
        required=True,
    )
    parser.add_argument(
        "-i", "--integration", type=Path, help="dump the integration diagram",
    )
    parser.add_argument(
        "--dump-stats",
        type=argparse.FileType("w"),
        nargs="?",
        const=sys.stdout,
        help="path to CSV file to dump verification statistics",
    )
    parser.add_argument(
        "--dump-timings",
        type=argparse.FileType("w"),
        nargs="?",
        const=sys.stdout,
        help="path to CSV file to dump verification timings",
    )
    parser.add_argument(
        "--no-output",
        help="validate only, do not create compiled files, useful for benchmarking",
        action="store_true",
    )
    parser.add_argument(
        "--slow-check", help="perform a slow check", action="store_true",
    )
    parser.add_argument(
        "--skip-testing", help="do not check traces", action="store_true",
    )
    return parser


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()


def parse_uses(uses_path: Optional[Path]) -> Dict[str, str]:
    if uses_path is None:
        return {}

    uses: Dict[str, str]
    with uses_path.open(mode="r") as f:
        uses = yaml.safe_load(f)

    if uses is None:
        return {}  # empty or commented yaml
    elif isinstance(uses, dict):
        return uses
    else:
        raise CompilationError(
            "Shelley parser error: uses file must be a valid dictionary"
        )


def parse() -> None:
    args: argparse.Namespace = get_args()

    settings.VERBOSE = args.verbosity
    if settings.VERBOSE:
        logger.setLevel(logging.DEBUG)

    logger.debug("Input yaml file: {0}".format(args.device))

    try:
        compile_shelley(
            args.device,
            parse_uses(args.uses),
            args.output,
            binary=args.binary,
            integration=args.integration,
            dump_stats=args.dump_stats,
            dump_timings=args.dump_timings,
            no_output=args.no_output,
            slow_check=args.slow_check,
            skip_testing=args.skip_testing,
        )
    except CompilationError as error:
        if settings.VERBOSE:
            logger.error(str(error), exc_info=settings.VERBOSE)
        sys.exit(str(error))

    logger.debug("OK!")
