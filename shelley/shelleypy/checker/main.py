import argparse
import logging
import os
import sys
from pathlib import Path

from shelley.ast.devices import Device
from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.shelleypy.checker import settings
from shelley.shelleypy.checker.exceptions import CompilationError, ShelleyPyError
from shelley.shelleypy.checker.optimize import optimize as fun_optimize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shelleypy")


def get_command_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compile shelley files")
    parser.add_argument(
        "input", nargs=1, type=Path, help="Path to the input system (Python file)"
    )
    parser.add_argument("-o", "--output", type=Path, help="path to store shelley file")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "--optimize",
        help="Try to merge operations that share the same next operations (BETA)",
        action="store_true",
    )
    parser.add_argument(
        "--use-old-checker",
        help="Uses the old checker algorithm instead of the new one (which uses the visitor pattern)",
        action="store_true",
    )
    return parser.parse_args()


def exit_with_error(lineno: int, msg: str):
    logger.error(f"{msg} (l. {lineno})")
    sys.exit(os.EX_SOFTWARE)


def shelley2lark(device: Device, output_path: Path):
    visitor = Shelley2Lark(components=device.components)
    device.accept(visitor)

    lark_code = visitor.result.strip()
    # print(lark_code)

    logger.debug(f"Dumping {output_path}")
    with output_path.open("w") as f:
        f.write(lark_code)


def check(src_path: Path, output_path: Path, optimize=False, use_old_checker=False):
    if use_old_checker:
        from shelley.shelleypy.checker.old_checker import python2shelley
    else:
        from shelley.shelleypy.checker.checker import python2shelley

    try:
        device = python2shelley(src_path, external_only=False)
        if optimize:
            fun_optimize(device)
        integration_output_path: Path = Path(output_path.parent, f"integration_{output_path.name}")
        shelley2lark(device, output_path=integration_output_path)

        device = python2shelley(src_path, external_only=True)
        shelley2lark(device, output_path=output_path)
    except ShelleyPyError as err:
        exit_with_error(err.lineno, err.msg)


def main() -> None:
    args: argparse.Namespace = get_command_args()

    settings.VERBOSE = args.verbosity
    if settings.VERBOSE:
        logger.setLevel(logging.DEBUG)

    input_path: Path = args.input[0]
    logger.debug("Input python file: {0}".format(Path.absolute(input_path)))

    try:
        check(
            src_path=input_path,
            output_path=args.output,
            optimize=args.optimize,
            use_old_checker=args.use_old_checker
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
