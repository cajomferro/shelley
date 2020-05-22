import logging
import argparse
import sys

from shelley.shelleyc import settings
from shelley.shelleyc.exceptions import CompilationError
from shelley.shelleyc import compile_shelley, get_args

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleyc")


def main() -> None:
    args: argparse.Namespace = get_args()

    settings.VERBOSE = args.verbosity
    if settings.VERBOSE:
        logger.setLevel(logging.DEBUG)

    logger.debug("Input yaml file: {0}".format(args.device))

    try:
        compile_shelley(
            args.device,
            args.uses,
            args.output,
            binary=args.binary,
            intermediate=args.intermediate,
            dump_stats=args.dump_stats,
            dump_timings=args.dump_timings,
            no_output=args.no_output,
            fast_check=args.fast_check,
            skip_testing=args.skip_testing,
        )
    except CompilationError as error:
        if settings.VERBOSE:
            logger.error(str(error), exc_info=settings.VERBOSE)
        sys.exit(str(error))

    logger.debug("OK!")


if __name__ == "__main__":
    main()
