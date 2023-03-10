import logging
import os
from typing import List, Dict, Optional, Any, cast, IO
from pathlib import Path
import yaml

from shelley.shelleyc import settings
from shelley.shelleyc.exceptions import CompilationError
from shelley.shelleyc.serializer import serialize, deserialize
from shelley.shelleyc.stats import save_timings

from shelley.automata import (
    CheckedDevice,
    AssembledDevice,
    check_traces,
    AssembledMicroBehavior,
)
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata

import shelley.parsers.shelley_lark_parser as lark_parser
import shelley.parsers.yaml.yaml2shelley as yaml_parser

logger = logging.getLogger("shelleyc")


class DeviceMapping:
    def __init__(
        self,
        *,
        files: Optional[Dict[str, Path]] = None,
        binary: bool = False,
        base_dir: Path = Path.cwd(),
    ):
        self.files = dict() if files is None else files
        self.binary = binary
        self.loaded: Dict[str, CheckedDevice] = dict()
        self.base_dir = base_dir

    def __getitem__(self, key):
        dev = self.loaded.get(key, None)
        if dev is not None:
            return dev
        try:
            fname = self.files[key]
            if not fname.is_absolute():
                fname = self.base_dir / fname
            self.loaded[key] = dev = deserialize(fname, self.binary)
            return dev
        except KeyError:
            raise CompilationError(f"Error loading system '{key}': system not defined")
        except (KeyError, IOError) as err:
            raise CompilationError(f"Error loading system '{key}': {err}")


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
                "Device {name} depends on {uses_device_name}. Please update uses file!".format(
                    name=device.name, uses_device_name=uses_device_name
                )
            )

    return known_devices


def _parse_uses(uses_path: Optional[Path]) -> Dict[str, str]:
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


def _get_ext(binary: bool = False) -> str:
    return (
        settings.EXT_SHELLEY_COMPILED_BIN
        if binary
        else settings.EXT_SHELLEY_COMPILED_YAML
    )


def dump_integration_model(dev: AssembledDevice, integration: Path, binary=False):
    logger.debug("Generating integration diagram...")

    assert isinstance(dev.internal, AssembledMicroBehavior)
    serialize(integration, dev.internal.nfa.as_dict(), binary)


def compile_shelley(
    *,
    src_path: Path,
    uses_path: Path,
    dst_path: Optional[Path] = None,
    binary: bool = False,
    integration: Optional[Path] = None,
    dump_timings: Optional[IO[str]] = None,
    save_output: bool = True,
    skip_testing: bool = True,
    skip_checks: bool = False,
    check_ambiguity: bool = False,
) -> AssembledDevice:
    """

    :param src_path: Shelley device src path to be compiled (YAML file)
    :param uses: list of paths to compiled dependencies (uses)
    :param dst_path: compiled file destination path
    :param binary: save as binary or as yaml
    :return:
    """

    src_ext = src_path.suffix.split(".")[1]
    if src_ext in settings.EXT_SHELLEY_SOURCE_YAML:
        try:
            shelley_device: ShelleyDevice = yaml_parser.get_shelley_from_yaml(src_path)
        except yaml_parser.ShelleyParserError as error:
            if settings.VERBOSE:
                logger.exception(error)
            raise CompilationError(f"YAML Parsing error: {error}")

    elif src_ext in settings.EXT_SHELLEY_SOURCE_LARK:
        try:
            shelley_device: ShelleyDevice = lark_parser.parse(src_path)
        except Exception as error:
            if settings.VERBOSE:
                logger.exception(error)
            raise CompilationError(f"Lark Parsing error: {error}")

    else:
        raise CompilationError(f"Unknown source type: {src_ext}")

    if dst_path is None:
        dst_path = src_path.parent / (src_path.stem + "." + _get_ext(binary))

    uses_base_dir = uses_path.parent if uses_path is not None else Path.cwd()
    uses = _parse_uses(uses_path)
    known_devices = DeviceMapping(
        files=dict((k, Path(v)) for (k, v) in uses.items()),
        binary=binary,
        base_dir=uses_base_dir,
    )
    automata_device = shelley2automata(shelley_device)

    try:
        dev = AssembledDevice.make(
            automata_device, known_devices.__getitem__, skip_checks, check_ambiguity
        )
    except ValueError as error:
        if settings.VERBOSE:
            logger.exception(error)
        raise CompilationError("Invalid device: {0}".format(str(error)))

    if dump_timings is not None:
        logger.debug("Dumping timings")
        save_timings(dump_timings, dev)

    if (
        integration is not None and dev.internal is not None
    ):  # do this only for compound devices
        dump_integration_model(dev, integration)

    if (skip_checks or dev.is_valid) and save_output:
        logger.debug("Compiling device: {0}".format(shelley_device.name))
        serialize(dst_path, dev.external.nfa.as_dict(), binary)
        logger.debug("Compiled file: {0}".format(dst_path))

    if skip_checks:
        logger.debug("Skip direct checks")
    else:
        # Do not ignore checks
        if dev.is_valid:
            if skip_testing:
                logger.debug("Skip testing traces")
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
        else:
            raise CompilationError("Invalid device: {0}".format(dev.failure))

    return shelley_device, dev
