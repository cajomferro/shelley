# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

import pytest

from .context import shelley

import yaml

from shelley.automata import Device as AutomataDevice, AssembledDevice, assemble_device, CheckedDevice, check_traces
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml


def get_shelley_device(name: str) -> ShelleyDevice:
    with open('tests/input/{0}.yml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    return create_device_from_yaml(yaml_code)


def test_button():
    shelley_device: ShelleyDevice = get_shelley_device('button')
    automata: AutomataDevice = shelley2automata(shelley_device)

    assembled_button: AssembledDevice = assemble_device(automata, {})
    assert type(assembled_button.external) == CheckedDevice

    # # test macro traces
    # check_traces(assembled_button.external.nfa, shelley_device.test_macro['ok'],
    #              shelley_device.test_macro['fail'])  # macro
    #
    # # test micro traces
    # check_traces(assembled_button.internal, shelley_device.test_micro['ok'],
    #              shelley_device.test_micro['fail'])  # micro


def test_smart_button():
    checked_button = assemble_device(shelley2automata(get_shelley_device('button')), {}).external
    assert type(checked_button) == CheckedDevice

    shelley_device = get_shelley_device('smartbutton1')
    automata = shelley2automata(shelley_device)
    assembled_smartbutton: AssembledDevice = assemble_device(automata, {'Button': checked_button})
    assert type(assembled_smartbutton.external) == CheckedDevice

    with pytest.raises(ValueError) as exc_info:
        # test micro traces
        check_traces(assembled_smartbutton.internal, {"good": ["b.released", "b.pressed"]}, {})  # micro

    assert str(exc_info.value) == "Unaccepted valid trace: good : ['b.released', 'b.pressed']"

    # # test macro traces
    # check_traces(assembled_smartbutton.external.nfa, shelley_device.test_macro['ok'],
    #              shelley_device.test_macro['fail'])  # macro
    #
    # # test micro traces
    # check_traces(assembled_smartbutton.internal, shelley_device.test_micro['ok'],
    #              shelley_device.test_micro['fail'])  # micro


def test_desklamp():
    dev = shelley2automata(get_shelley_device('desklamp'))
    known_devices = {'Led': assemble_device(shelley2automata(get_shelley_device('led')), {}).external,
                     'Button': assemble_device(shelley2automata(get_shelley_device('button')), {}).external,
                     'Timer': assemble_device(shelley2automata(get_shelley_device('timer')), {}).external}
    assert type(assemble_device(dev, known_devices).external) == CheckedDevice
