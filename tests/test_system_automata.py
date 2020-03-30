# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

import yaml

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    with open('tests/input/{0}.yaml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley2automata(shelley)


def test_smart_button():
    button = check_valid_device(_get_automata_from_yaml('button'), {})
    assert type(button) == CheckedDevice

    smartbutton = check_valid_device(_get_automata_from_yaml('smartbutton1'), {'Button': button})
    assert type(smartbutton) == CheckedDevice

    # print(button.nfa.flatten())
    # print(smartbutton.nfa.flatten())


def test_desklamp():
    dev = _get_automata_from_yaml('desklamp')
    known_devices = {'Led': check_valid_device(_get_automata_from_yaml('led'), {}),
                     'Button': check_valid_device(_get_automata_from_yaml('button'), {}),
                     'Timer': check_valid_device(_get_automata_from_yaml('timer'), {})}
    assert type(check_valid_device(dev, known_devices)) == CheckedDevice
