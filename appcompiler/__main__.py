import logging
import os
import sys

from .context import shelley

from . import settings
from . import compile_shelley, get_args, CompilationError, get_shelley_from_yaml

from shelley.ast.devices import Device as ShelleyDevice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(args):
    # print(args)

    settings.SRC_FILEPATH = os.path.realpath(args.device)  # --device
    settings.SRC_BASENAME = os.path.splitext(os.path.basename(settings.SRC_FILEPATH))[0]

    if args.outdir is None:
        settings.OUTPUT_DIR = os.path.dirname(settings.SRC_FILEPATH)
    else:  # if --output is specified, create folder if doesn't exist yet
        settings.OUTPUT_DIR = os.path.realpath(args.outdir)
        try:
            os.mkdir(settings.OUTPUT_DIR)
        except FileExistsError:
            pass

    try:
        shelley_device: ShelleyDevice = get_shelley_from_yaml(settings.SRC_FILEPATH)
    except FileNotFoundError as error:
        logger.error("Device {0} not found!".format(settings.SRC_FILEPATH), exc_info=settings.VERBOSE)
        sys.exit()

    settings.DEVICE_NAME = shelley_device.name

    if args.binary:
        settings.DST_FILEPATH = os.path.join(settings.OUTPUT_DIR,
                                             '{0}.{1}'.format(settings.SRC_BASENAME, settings.EXT_SHELLEY_COMPILED_BIN))
    else:
        settings.DST_FILEPATH = os.path.join(settings.OUTPUT_DIR,
                                             '{0}.{1}'.format(settings.SRC_BASENAME,
                                                              settings.EXT_SHELLEY_COMPILED_YAML))

    if args.verbosity:
        settings.VERBOSE = True
        logger.setLevel(logging.DEBUG)

    #    if args.name is not None:
    #        assert args.name == settings.DEVICE_NAME

    logger.debug('Compiling device {0}...'.format(settings.DEVICE_NAME))
    logger.debug('Input yaml file: {0}'.format(settings.SRC_FILEPATH))

    try:
        compile_shelley(shelley_device, args.uses, settings.DST_FILEPATH, binary=args.binary)
    except CompilationError as error:
        logger.error(str(error), exc_info=settings.VERBOSE)
        sys.exit()
    except FileNotFoundError as error:
        logger.error(str(error), exc_info=settings.VERBOSE)
        sys.exit()

    logger.debug('Compiled file: {0}'.format(settings.DST_FILEPATH))
    print('OK!')


if __name__ == "__main__":
    main(get_args())
