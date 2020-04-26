import logging
import argparse
import sys

import shelley

from . import settings
from .exceptions import CompilationError
from . import compile_shelley, get_args

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    if args.verbosity:
        settings.VERBOSE = True
        logger.setLevel(logging.DEBUG)

    # src_basename = os.path.splitext(os.path.basename(src_filepath))[0]

    logger.debug('Input yaml file: {0}'.format(args.device))

    try:
        compile_shelley(args.device, args.uses, args.output, binary=args.binary, intermediate=args.intermediate)
    except CompilationError as error:
        if settings.VERBOSE:
            logger.error(str(error), exc_info=settings.VERBOSE)
        sys.exit(str(error))

    logger.debug('OK!')


if __name__ == "__main__":
    main(get_args())
