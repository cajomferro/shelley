import logging
import yaml
import os
import typing
import argparse
from pathlib import Path

from .context import shelley

from . import settings
from .exceptions import CompilationError
from .serializer import serialize, deserialize

from shelley.automata import assemble_device, CheckedDevice, AssembledDevice, check_traces
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def create_parser():
#     parser = argparse.ArgumentParser(description='Compile shelley files')
#     parser.add_argument("src", metavar='source', help="Path to the input example yaml file")
#     parser.add_argument("name", metavar='name', help="Device name", nargs='?')
#     parser.add_argument("-u", "--uses", action='append', nargs=2, help="path to used device")
#     parser.add_argument("-o", "--outdir", nargs=1, help="path to store compiled files")
#     parser.add_argument("-b", "--binary", help="generate binary files", action='store_true')
#     return parser

def create_parser():
    parser = argparse.ArgumentParser(description='Compile shelley files')
    parser.add_argument("-v", "--verbosity", help="increase output verbosity", action='store_true')
    parser.add_argument("-u", "--uses", nargs='*', default=[], help="path to used device")
    parser.add_argument("-o", "--output", type=Path, help="path to store compile file")
    parser.add_argument("-b", "--binary", help="generate binary files", action='store_true')
    parser.add_argument("-d", '--device', type=Path, help="Path to the input example yaml file", required=True)
    return parser


def get_dest_path(args_binary: bool, args_output_dir: str, args_src_filepath: str, device_name: str) -> str:
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
        dest_path = os.path.join(output_dir, '{0}.{1}'.format(device_name, settings.EXT_SHELLEY_COMPILED_BIN))
    else:
        dest_path = os.path.join(output_dir, '{0}.{1}'.format(device_name, settings.EXT_SHELLEY_COMPILED_YAML))

    return dest_path


def get_shelley_from_yaml(path: Path) -> ShelleyDevice:
    with open(path, 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley


def _get_known_devices(device: ShelleyDevice, uses_list: typing.List[str], binary=False) -> typing.Mapping[
    str, CheckedDevice]:
    known_devices: typing.Mapping[str, CheckedDevice] = dict()
    for u in uses_list:
        try:
            device_path, device_name = u.split(settings.USE_DEVICE_NAME_SEP)
        except ValueError as error:
            if settings.VERBOSE:
                logger.exception(error)
            raise CompilationError('Invalid dependency: {0}. Perhaps missing device name?'.format(u))
        known_devices[device_name] = deserialize(device_path, binary)

    if len(device.uses) != len(known_devices):
        raise CompilationError('Device {name} expects {uses} but found {known_devices}!'.format(
            name=device.name, uses=device.uses, known_devices=list(known_devices.keys())))

    for dname in device.uses:  # check that all uses match the specified dependencies on the command
        if dname not in known_devices:
            raise CompilationError('Device dependency not specified: {0}!'.format(dname))

    return known_devices


def compile_shelley(src_path: Path, uses: typing.List[str], dst_path: Path = None, binary=False) -> Path:
    """

    :param device: Shelley device src path to be compiled
    :param uses: list of paths to compiled dependencies (uses)
    :param outdir: optional output dir path (if not specified, same as src)
    :param binary: save as binary or as yaml
    :return:
    """
    shelley_device: ShelleyDevice = get_shelley_from_yaml(src_path)
    if dst_path is None:
        ext = settings.EXT_SHELLEY_COMPILED_BIN if binary else settings.EXT_SHELLEY_COMPILED_YAML
        dst_path = src_path.parent / (src_path.stem + "." + ext)

    logger.debug('Compiling device: {0}'.format(shelley_device.name))

    known_devices: typing.Mapping[str, CheckedDevice] = _get_known_devices(shelley_device, uses, binary)
    automata_device = shelley2automata(shelley_device)

    checked_device = assemble_device(automata_device, known_devices)

    if isinstance(checked_device, AssembledDevice):

        # test macro traces
        check_traces(checked_device.external.nfa, shelley_device.test_macro['ok'],
                     shelley_device.test_macro['fail'])  # macro

        # test micro traces
        check_traces(checked_device.internal, shelley_device.test_micro['ok'],
                     shelley_device.test_micro['fail'])  # micro

        serialize(dst_path, checked_device.external, binary)
    else:
        raise CompilationError("Invalid device: {0}".format(checked_device))

    logger.debug('Compiled file: {0}'.format(dst_path))

    return dst_path


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()
