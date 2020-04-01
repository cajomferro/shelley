# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

import yaml
import os

from karakuri import regular

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml
from shelley.compiler import deserialize_checked_device, deserialize_checked_device_binary, serialize_checked_device, \
    serialize_checked_device_binary

COMPILED_FILES_PATH = 'tests/compiled/'


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    with open('examples/{0}.yaml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley2automata(shelley)


def _get_compiled_path(name: str, binary=False):
    if binary:
        ext = 'pickle'
    else:
        ext = 'yml'
    try:
        os.mkdir(COMPILED_FILES_PATH)
    except FileExistsError:
        pass
    return os.path.join(os.path.realpath(COMPILED_FILES_PATH), '{0}.{1}'.format(name, ext))


def test_button():
    name = 'button'
    path = _get_compiled_path(name)
    checked_device = check_valid_device(_get_automata_from_yaml(name), {})
    assert type(checked_device) == CheckedDevice

    serialize_checked_device(path, checked_device)
    assert os.path.exists(path)

    deserialized_device = deserialize_checked_device(path)

    #    os.remove(path)
    #    assert os.path.exists(path) is False

    dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
    print(dfa_checked_device)
    dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)
    print(dfa_deserialized_device)

    assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)


def test_button_binary():
    name = 'button'
    path = _get_compiled_path(name, binary=True)
    checked_device = check_valid_device(_get_automata_from_yaml(name), {})
    assert type(checked_device) == CheckedDevice

    serialize_checked_device_binary(path, checked_device)
    assert os.path.exists(path)

    deserialized_device = deserialize_checked_device_binary(path)

    #    os.remove(path)
    #    assert os.path.exists(path) is False

    dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
    dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)

    assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)
