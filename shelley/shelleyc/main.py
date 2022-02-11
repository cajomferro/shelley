from typing import Dict, Optional
from pathlib import Path
import logging
import argparse
import sys
import yaml

from shelley.shelleyc import settings
from shelley.shelleyc.exceptions import CompilationError
from shelley.shelleyc import shelleyc

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
        "-i",
        "--integration",
        type=Path,
        help="dump the integration diagram",
    )
    parser.add_argument(
        "--dump-timings",
        type=argparse.FileType("w"),
        nargs="?",
        const=sys.stdout,
        help="path to JSON file to dump verification timings",
    )
    parser.add_argument(
        "--no-output",
        dest="save_output",
        help="validate only, do not create compiled files, useful for benchmarking",
        action="store_false",
    )
    parser.add_argument(
        "--skip-testing",
        help="do not check traces",
        action="store_true",
    )
    parser.add_argument(
        "--skip-checks",
        help="Skip validity tests.",
        action="store_true",
    )
    parser.add_argument(
        "--check-ambiguity",
        help="Also check ambiguity.",
        action="store_true",
    )
    return parser


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()


def parse() -> None:
    args: argparse.Namespace = get_args()

    settings.VERBOSE = args.verbosity
    if settings.VERBOSE:
        logger.setLevel(logging.DEBUG)

    logger.debug("Input yaml file: {0}".format(args.device))

    try:
        shelleyc.compile_shelley(
            src_path=args.device,
            uses_path=args.uses,
            dst_path=args.output,
            binary=args.binary,
            integration=args.integration,
            dump_timings=args.dump_timings,
            save_output=args.save_output,
            skip_testing=args.skip_testing,
            skip_checks=args.skip_checks,
            check_ambiguity=args.check_ambiguity,
        )
        logger.debug("OK!")
    except CompilationError as error:
        if settings.VERBOSE:
            logger.error(str(error), exc_info=settings.VERBOSE)
        else:
            print(str(error), file=sys.stderr)
        logger.debug("ERROR!")
        sys.exit(1)


def main() -> None:
    parse()


if __name__ == "__main__":
    main()
