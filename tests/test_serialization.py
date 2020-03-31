# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

import yaml
import dill
import os
import typing

from karakuri import regular

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml

COMPILED_FILES_PATH = 'tests/compiled/'


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    with open('tests/input/{0}.yaml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley2automata(shelley)


def _serialize_checked_device(path: str, device: CheckedDevice) -> typing.NoReturn:
    with open(path, 'wb') as f:
        dill.dump(device, f, dill.HIGHEST_PROTOCOL)


def _deserialize_checked_device(path: str) -> CheckedDevice:
    with open(path, 'rb') as f:
        device = dill.load(f)
    return device


def test_button():
    name = 'button'
    path = os.path.join(os.path.realpath(COMPILED_FILES_PATH), '{0}.pickle'.format(name))
    checked_device = check_valid_device(_get_automata_from_yaml(name), {})
    assert type(checked_device) == CheckedDevice

    _serialize_checked_device(path, checked_device)
    assert os.path.exists(path)

    deserialized_device = _deserialize_checked_device(path)

#    os.remove(path)
#    assert os.path.exists(path) is False

    dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
    dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)

    assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)
