import logging
import yaml
import os
import typing
import argparse

from .context import shelley

from . import settings
from .exceptions import CompilationError
from .serializer import serialize, deserialize

from shelley.automata import assemble_device, CheckedDevice, AssembledDevice
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
    parser.add_argument("-o", "--outdir", help="path to store compiled files")
    parser.add_argument("-b", "--binary", help="generate binary files", action='store_true')
    parser.add_argument("-d", '--device', help="Path to the input example yaml file", required=True)
    return parser


def get_shelley_from_yaml(path: str) -> ShelleyDevice:
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


#    known_devices = dict()
#    for d in device.uses:
#        known_devices[device_name] = _find_compiled_device(device_name)
#    return known_devices


def compile_shelley(device: ShelleyDevice, uses: typing.List[str], dst_path: str, binary=False):
    """

    :param device: Shelley device to be compiled
    :param uses: list of paths to compiled dependencies (uses)
    :param dst_path: destination path to compiled shelley device
    :param binary: save as binary or as yaml
    :return:
    """
    known_devices: typing.Mapping[str, CheckedDevice] = _get_known_devices(device, uses, binary)
    automata_device = shelley2automata(device)

    checked_device = assemble_device(automata_device, known_devices)

    if isinstance(checked_device, AssembledDevice):
        serialize(dst_path, checked_device.external, binary)
    else:
        raise CompilationError("Invalid device: {0}".format(checked_device))


def get_args() -> argparse.Namespace:
    return create_parser().parse_args()
