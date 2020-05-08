import sys
import logging
import os
from typing import List, Dict, Optional, Any, cast, IO
import argparse
from pathlib import Path
from karakuri import regular


from shelley.shelleyc import settings
from shelley.shelleyc.exceptions import CompilationError
from shelley.shelleyc.serializer import serialize, deserialize
from shelley.shelleyc.stats import save_statistics, save_timings

from shelley.automata import (
    CheckedDevice,
    AssembledDevice,
    check_traces,
    AssembledMicroBehavior,
)
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley import yaml2shelley


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile shelley files")
    parser.add_argument(
        "-v", "--verbosity", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-u", "--uses", nargs="*", default=[], help="path to used device"
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
    return parser


def get_dest_path(
    args_binary: bool, args_output_dir: str, args_src_filepath: str, device_name: str
) -> str:
    if args_output_dir is None:
        output_dir = os.path.dirname(args_src_filepath)
    else:  # if --output is specified, create folder if doesn't exist yet
        output_dir = os.path.realpath(args_output_dir)
        try:
            os.mkdir(output_dir)
        except FileExistsError:
            pass

    dest_path: str
    if args_binary:
        dest_path = os.path.join(
            output_dir, "{0}.{1}".format(device_name, settings.EXT_SHELLEY_COMPILED_BIN)
        )
    else:
        dest_path = os.path.join(
            output_dir,
            "{0}.{1}".format(device_name, settings.EXT_SHELLEY_COMPILED_YAML),
        )

    return dest_path


def _get_known_devices(
    device: ShelleyDevice, uses_list: List[str], binary: bool = False
) -> Dict[str, CheckedDevice]:
    known_devices: Dict[str, CheckedDevice] = {}
    for u in uses_list:
        try:
            device_path, device_name = u.split(settings.USE_DEVICE_NAME_SEP)
        except ValueError as error:
            if settings.VERBOSE:
                logger.exception(error)
            raise CompilationError(
                "Invalid dependency: {0}. Perhaps missing device name?".format(u)
            )
        known_devices[device_name] = deserialize(Path(device_path), binary)

    if len(device.uses) != len(known_devices):
        raise CompilationError(
            "Device {name} expects {uses} but found {known_devices}!".format(
                name=device.name,
                uses=device.uses,
                known_devices=list(known_devices.keys()),
            )
        )

    for (
        dname
    ) in (
        device.uses
    ):  # check that all uses match the specified dependencies on the command
        if dname not in known_devices:
            raise CompilationError(
                "Device dependency not specified: {0}!".format(dname)
            )

    return known_devices


def _get_ext(binary: bool = False) -> str:
    return (
        settings.EXT_SHELLEY_COMPILED_BIN
        if binary
        else settings.EXT_SHELLEY_COMPILED_YAML
    )


def compile_shelley(
    src_path: Path,
    uses: List[str],
    dst_path: Optional[Path] = None,
    binary: bool = False,
    intermediate: bool = False,
    dump_stats: Optional[IO[str]] = None,
    dump_timings: Optional[IO[str]] = None,
    no_output: bool = False,
) -> Path:
    """

    :param src_path: Shelley device src path to be compiled (YAML file)
    :param uses: list of paths to compiled dependencies (uses)
    :param dst_path: compiled file destination path
    :param binary: save as binary or as yaml
    :return:
    """

    try:
        shelley_device: ShelleyDevice = yaml2shelley.get_shelley_from_yaml(src_path)
    except yaml2shelley.ShelleyParserError as error:
        if settings.VERBOSE:
            logger.exception(error)
        raise CompilationError("Shelley parser error: {0}".format(str(error)))

    if dst_path is None:
        dst_path = src_path.parent / (src_path.stem + "." + _get_ext(binary))

    logger.debug("Compiling device: {0}".format(shelley_device.name))

    known_devices: Dict[str, CheckedDevice] = _get_known_devices(
        shelley_device, uses, binary
    )
    automata_device = shelley2automata(shelley_device)
    dev = AssembledDevice.make(automata_device, known_devices)

    if dump_stats is not None:
        save_statistics(dump_stats, dev)

    if dump_timings is not None:
        save_timings(dump_timings, dev)

    if dev.is_valid:
        try:
            # test macro traces
            check_traces(dev.external_model_check, shelley_device.test_macro)  # macro

            # test micro traces
            check_traces(dev.internal_model_check, shelley_device.test_micro)  # micro
        except ValueError as err:
            raise CompilationError(str(err))

        if not no_output:
            serialize(dst_path, dev.external.nfa.as_dict(), binary)

            if intermediate is True and dev.internal is not None:
                micro: AssembledMicroBehavior = dev.internal

                # generate shuffling of all components
                path = src_path.parent / (
                    src_path.stem + "-shuffle-dfa" + "." + _get_ext(binary)
                )
                shuffle = regular.dfa_to_nfa(
                    micro.possible
                ).remove_all_sink_states()  # without traps
                serialize(path, shuffle.as_dict(), binary)

                # generate internal nfa without epsilon and without traps
                path = src_path.parent / (
                    src_path.stem + "-internal-nfa" + "." + _get_ext(binary)
                )
                nfa = micro.nfa.remove_epsilon_transitions().remove_all_sink_states()
                serialize(path, nfa.as_dict(), binary)

                # generate internal minimized dfa without traps (must be converted to NFA)
                path = src_path.parent / (
                    src_path.stem + "-internal-dfa" + "." + _get_ext(binary)
                )
                nfa = regular.dfa_to_nfa(
                    cast(regular.DFA[Any, str], micro.dfa.minimize())
                ).remove_all_sink_states()
                serialize(path, nfa.as_dict(), binary)

    else:
        raise CompilationError("Invalid device: {0}".format(dev.failure))

    logger.debug("Compiled file: {0}".format(dst_path))

    return dst_path
