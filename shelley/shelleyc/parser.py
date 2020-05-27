from typing import List, Optional
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
    parser_uses_group = parser.add_mutually_exclusive_group()
    parser_uses_group.add_argument(
        "-u", "--uses", nargs="*", default=[], help="path to used device"
    )
    parser_uses_group.add_argument(
        "-uf", "--uses-file", type=Path, default=None, help="path to file with uses"
    )
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
        "-i",
        "--intermediate",
        help="export intermediate structures representations",
        action="store_true",
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


def parse_uses(uses_list: List[str], uses_file: Optional[Path]) -> List[str]:
    if uses_file is None:
        return uses_list

    uses: List[str]
    with uses_file.open(mode="r") as f:
        uses = yaml.safe_load(f)
    return uses


def parse() -> None:
    args: argparse.Namespace = get_args()

    settings.VERBOSE = args.verbosity
    if settings.VERBOSE:
        logger.setLevel(logging.DEBUG)

    logger.debug("Input yaml file: {0}".format(args.device))

    try:
        compile_shelley(
            args.device,
            parse_uses(args.uses, args.uses_file),
            args.output,
            binary=args.binary,
            intermediate=args.intermediate,
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
