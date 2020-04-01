# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

import typing
import yaml
import os

from karakuri import regular

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml
from shelley.compiler import deserialize_checked_device, deserialize_checked_device_binary, serialize_checked_device, \
    serialize_checked_device_binary

COMPILED_FILES_PATH = 'examples/compiled'
EXAMPLES_PATH = 'examples'


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    with open('{0}/{1}.yaml'.format(EXAMPLES_PATH, name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley2automata(shelley)


def _get_compiled_path(name: str, binary=False):
    if binary:
        ext = 'shelcb'
    else:
        ext = 'shelc'
    try:
        os.mkdir(COMPILED_FILES_PATH)
    except FileExistsError:
        pass
    return os.path.join(os.path.realpath(COMPILED_FILES_PATH), '{0}.{1}'.format(name, ext))


def _serialize_device(name, known_devices: typing.Mapping[str, CheckedDevice] = {}, binary=False) -> CheckedDevice:
    path = _get_compiled_path(name, binary=True)
    checked_device = check_valid_device(_get_automata_from_yaml(name), known_devices)
    if binary:
        serialize_checked_device_binary(path, checked_device)
    else:
        serialize_checked_device(path, checked_device)
    return checked_device


def test_button():
    name = 'button'

    # serialize and deserialize (yaml)
    path = _get_compiled_path(name, binary=False)
    checked_device = _serialize_device(name, binary=False)
    deserialized_device = deserialize_checked_device(path)

    # compare original to deserialized
    dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
    dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)
    assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)

    os.remove(path)


def test_button_binary():
    name = 'button'

    # serialize and deserialize (dill)
    path = _get_compiled_path(name, binary=True)
    checked_device = _serialize_device(name, binary=True)
    deserialized_device = deserialize_checked_device_binary(path)

    # compare original to deserialized
    dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
    # print(dfa_checked_device)
    dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)
    # print(dfa_deserialized_device)
    assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)

    os.remove(path)


def test_smartbutton1_binary():
    name = 'smartbutton1'

    _serialize_device('button', binary=True)

    button_path = _get_compiled_path('button', binary=True)
    known_devices = {
        'Button': deserialize_checked_device_binary(button_path)
    }
    os.remove(button_path)

    # serialize and deserialize (dill)
    path = _get_compiled_path(name, binary=True)
    checked_device = _serialize_device(name, known_devices, binary=True)
    deserialized_device = deserialize_checked_device_binary(path)

    # compare original to deserialized
    dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
    # print(dfa_checked_device)
    dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)
    # print(dfa_deserialized_device)
    assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)

    os.remove(path)
