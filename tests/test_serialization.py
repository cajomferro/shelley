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
from appcompiler.serializer import _deserialize_checked_device, _deserialize_checked_device_binary, _serialize_checked_device, \
    _serialize_checked_device_binary

COMPILED_FILES_PATH = 'tests/compiled'
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
    path = _get_compiled_path(name, binary=binary)
    checked_device = check_valid_device(_get_automata_from_yaml(name), known_devices)
    if binary:
        _serialize_checked_device_binary(path, checked_device)
    else:
        _serialize_checked_device(path, checked_device)
    return checked_device


def _test_button(binary=False):
    name = 'button'

    # serialize and deserialize (yaml)
    path = _get_compiled_path(name, binary=binary)
    checked_device = _serialize_device(name, binary=binary)
    if binary:
        deserialized_device = _deserialize_checked_device_binary(path)
    else:
        deserialized_device = _deserialize_checked_device(path)

    assert deserialized_device.nfa == checked_device.nfa


def _test_smartbutton1(binary=False):
    # serialize and deserialize button

    _serialize_device('button', binary=binary)
    button_path = _get_compiled_path('button', binary=binary)

    if binary:
        button_device = _deserialize_checked_device_binary(button_path)
    else:
        button_device = _deserialize_checked_device(button_path)

    known_devices = {
        'Button': button_device
    }

    # serialize and deserialize smartbutton
    path = _get_compiled_path('smartbutton1', binary=binary)
    checked_device = _serialize_device('smartbutton1', known_devices, binary=binary)
    if binary:
        deserialized_device = _deserialize_checked_device_binary(path)
    else:
        deserialized_device = _deserialize_checked_device(path)

    assert deserialized_device.nfa == checked_device.nfa


def test_button():
    _test_button(binary=False)


def test_button_binary():
    _test_button(binary=True)


def test_smartbutton1():
    _test_smartbutton1(binary=False)


def test_smartbutton1_binary():
    _test_smartbutton1(binary=True)
