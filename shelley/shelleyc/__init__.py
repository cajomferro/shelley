import logging
import os
from typing import List, Dict, Optional, Any, cast, IO
from pathlib import Path

from shelley.shelleyc import settings
from shelley.shelleyc.exceptions import CompilationError
from shelley.shelleyc.serializer import serialize, deserialize
from shelley.shelleyc.stats import save_statistics, save_timings

from shelley.automata import (
    CheckedDevice,
    AssembledDevice,
    check_traces,
    AssembledMicroBehavior,
    AssembledMicroBehavior2,
)
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley import yaml2shelley


logger = logging.getLogger("shelleyc")


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
    device: ShelleyDevice, uses: Dict[str, str], binary: bool = False
) -> Dict[str, CheckedDevice]:
    known_devices: Dict[str, CheckedDevice] = {}

    for uses_device_name in device.uses:
        try:
            known_devices[uses_device_name] = deserialize(
                Path(uses[uses_device_name]), binary
            )
        except KeyError as err:
            raise CompilationError(
                "Device {name} dependency on {uses_device_name} not declared in uses file!".format(
                    name=device.name, uses_device_name=uses_device_name
                )
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
    uses: Dict[str, str],
    dst_path: Optional[Path] = None,
    binary: bool = False,
    integration: Optional[Path] = None,
    dump_stats: Optional[IO[str]] = None,
    dump_timings: Optional[IO[str]] = None,
    no_output: bool = False,
    slow_check: bool = False,
    skip_testing: bool = False,
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

    if slow_check:
        logger.debug("Performing slow check")

    try:
        dev = AssembledDevice.make(
            automata_device, known_devices, fast_check=not slow_check
        )
    except ValueError as error:
        if settings.VERBOSE:
            logger.exception(error)
        raise CompilationError("Shelley parser error: {0}".format(str(error)))

    if dump_stats is not None:
        logger.debug("Dumping statistics")
        save_statistics(dump_stats, dev)

    if dump_timings is not None:
        logger.debug("Dumping timings")
        save_timings(dump_timings, dev)

    if dev.is_valid:
        if skip_testing:
            logger.debug("Skipping tests")
        else:
            try:
                # test macro traces
                logger.debug("Testing macro traces")
                check_traces(
                    dev.external_model_check, shelley_device.test_macro
                )  # macro

                # test micro traces
                logger.debug("Testing micro traces")
                check_traces(
                    dev.internal_model_check, shelley_device.test_micro
                )  # micro
            except ValueError as err:
                raise CompilationError(str(err))

    if not no_output:
        serialize(dst_path, dev.external.nfa.as_dict(), binary)
        logger.debug("Compiled file: {0}".format(dst_path))

    if (
        integration is not None and dev.internal is not None
    ):  # do this only for compound devices
        logger.debug("Generating integration diagram...")

        assert isinstance(dev.internal, AssembledMicroBehavior) or isinstance(
            dev.internal, AssembledMicroBehavior2
        )
        serialize(integration, dev.internal.nfa.as_dict(), binary)

    if not dev.is_valid:
        raise CompilationError("Invalid device: {0}".format(dev.failure))

    return dst_path
