import yaml
import os
import sys
import typing
import argparse

from .context import shelley

from . import settings
from . import get_args

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml
from shelley.compiler import deserialize_checked_device, deserialize_checked_device_binary, serialize_checked_device, \
    serialize_checked_device_binary


def _get_shelley_from_yaml(path: str) -> ShelleyDevice:
    with open(path, 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley


def _find_compiled_device(path: str) -> CheckedDevice:
    # if os.path.splitext(path)[1] == '.shelcb':
    try:
        deserialized_device: CheckedDevice = deserialize_checked_device(path)
    except FileNotFoundError:
        sys.exit('{0} not found! Please compile it first!'.format(path))

    return deserialized_device


def _get_known_devices(device: ShelleyDevice, uses_list: typing.List[str]) -> typing.Mapping[str, CheckedDevice]:
    known_devices: typing.Mapping[str, CheckedDevice] = dict()
    for u in uses_list:
        device_path, device_name = u.split(':')
        known_devices[device_name] = _find_compiled_device(device_path)
        # print("{0},{1}".format(device_path, device_name))

    assert len(device.uses) == len(known_devices)
    for dname in device.uses:  # check that all uses match the specified dependencies on the command
        if dname not in known_devices:
            sys.exit('Device dependency not specified: {0}!'.format(dname))


#    known_devices = dict()
#    for d in device.uses:
#        known_devices[device_name] = _find_compiled_device(device_name)
#    return known_devices


def _compile(automata_device: AutomataDevice, known_devices: typing.Mapping[str, CheckedDevice], dst_path: str,
             binary=False):
    checked_device = check_valid_device(automata_device, known_devices)

    if type(checked_device) == CheckedDevice:
        if binary:
            serialize_checked_device_binary(dst_path, checked_device)
        else:
            serialize_checked_device(dst_path, checked_device)
    else:
        sys.exit("Invalid device!")


def main(args):
    # print(args)

    settings.SRC_FILEPATH = os.path.realpath(args.source)  # --source
    settings.SRC_BASENAME = os.path.splitext(os.path.basename(settings.SRC_FILEPATH))[0]

    if args.outdir is None:
        settings.OUTPUT_DIR = os.path.dirname(settings.SRC_FILEPATH)
    else:  # if --output is specified, create folder if doesn't exist yet
        settings.OUTPUT_DIR = os.path.realpath(args.outdir)
        try:
            os.mkdir(settings.OUTPUT_DIR)
        except FileExistsError:
            pass

    shelley_device: ShelleyDevice = _get_shelley_from_yaml(settings.SRC_FILEPATH)
    settings.DEVICE_NAME = shelley_device.name

    if args.binary is True:
        settings.DST_FILEPATH = os.path.join(settings.OUTPUT_DIR, '{0}.shelcb'.format(settings.SRC_BASENAME))
    else:
        settings.DST_FILEPATH = os.path.join(settings.OUTPUT_DIR, '{0}.shelc'.format(settings.SRC_BASENAME))

    #    if args.name is not None:
    #        assert args.name == settings.DEVICE_NAME

    print('Compiling device {0}...'.format(settings.DEVICE_NAME))
    print('Input yaml file: {0}'.format(settings.SRC_FILEPATH))

    known_devices: typing.Mapping[str, CheckedDevice] = _get_known_devices(shelley_device, args.uses)

    automata_device = shelley2automata(shelley_device)

    _compile(automata_device, known_devices, settings.DST_FILEPATH, binary=args.binary)

    print('Compiled file: {0}'.format(settings.DST_FILEPATH))
    print('OK!')


if __name__ == "__main__":
    main(get_args())
