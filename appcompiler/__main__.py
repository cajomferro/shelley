import yaml
import os
import sys
import typing

from .context import shelley

from . import settings

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml
from shelley.compiler import _deserialize_checked_device, _serialize_checked_device


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    path = os.path.join(settings.YAML_EXAMPLES_DIR, '{0}.yaml'.format(name))
    with open(path, 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley


def _find_compiled_device(name: str) -> CheckedDevice:
    path = os.path.join(settings.COMPILED_FILES_DIR, '{0}.pickle'.format(name.lower()))
    try:
        deserialized_device: CheckedDevice = _deserialize_checked_device(path)
    except FileNotFoundError:
        sys.exit('{0}.pickle not found! Please compile it first!'.format(name.lower()))
    print('Found dependency: {0}'.format(name))
    return deserialized_device


def _get_known_devices(device: ShelleyDevice) -> typing.Mapping[str, CheckedDevice]:
    known_devices = dict()
    for device_name in device.uses:
        known_devices[device_name] = _find_compiled_device(device_name)
    return known_devices


def _compile():
    current_device: ShelleyDevice = _get_automata_from_yaml(settings.DEVICE_NAME)

    automata_device: AutomataDevice = shelley2automata(current_device)
    known_devices: typing.Mapping[str, CheckedDevice] = _get_known_devices(current_device)

    checked_device = check_valid_device(automata_device, known_devices)

    if type(checked_device) == CheckedDevice:
        _serialize_checked_device(settings.COMPILED_FILE_PATH, checked_device)
    else:
        sys.exit("Invalid device!")

    assert os.path.exists(settings.COMPILED_FILE_PATH)


def main():
    try:
        os.mkdir(settings.COMPILED_FILES_DIR)
    except FileExistsError:
        pass

    try:
        settings.DEVICE_PATH = os.path.realpath(sys.argv[1])
    except IndexError:
        sys.exit('Please specify the path to the yaml file!')
    settings.DEVICE_NAME = os.path.splitext(os.path.basename(settings.DEVICE_PATH))[0]
    settings.COMPILED_FILE_PATH = os.path.join(os.path.realpath(settings.COMPILED_FILES_DIR),
                                               '{0}.pickle'.format(settings.DEVICE_NAME))
    print('Compiling {0}...'.format(settings.DEVICE_NAME))
    print('Input yaml path: {0}'.format(settings.DEVICE_PATH))

    _compile()

    print('Compiled file: {0}'.format(settings.COMPILED_FILE_PATH))
    print('OK!')


# deserialized_device = _deserialize_checked_device(path)

#    os.remove(path)
#    assert os.path.exists(path) is False

# dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
# dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)

# assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)


if __name__ == "__main__":
    main()
