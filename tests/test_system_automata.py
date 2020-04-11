# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from typing import Mapping, List

from .context import shelley

import yaml

from shelley.automata import Device as AutomataDevice, AssembledDevice, assemble_device, CheckedDevice, NFA
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml


def get_shelley_device(name: str) -> ShelleyDevice:
    with open('tests/input/{0}.yml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    return create_device_from_yaml(yaml_code)


def check_traces(nfa: NFA, test_ok: Mapping[str, List[str]], test_fail: Mapping[str, List[str]]):
    for key in test_ok:
        assert nfa.accepts(test_ok[key])

    for key in test_fail:
        assert not nfa.accepts(test_fail[key])


def test_button():
    shelley_device: ShelleyDevice = get_shelley_device('button')
    automata: AutomataDevice = shelley2automata(shelley_device)

    checked_button: CheckedDevice = assemble_device(automata, {}).external
    assert type(checked_button) == CheckedDevice

    check_traces(checked_button.nfa, shelley_device.test_macro['ok'], shelley_device.test_macro['fail'])


def test_smart_button():
    checked_button = assemble_device(shelley2automata(get_shelley_device('button')), {}).external
    assert type(checked_button) == CheckedDevice

    shelley_device = get_shelley_device('smartbutton1')
    automata = shelley2automata(shelley_device)
    assembled_smartbutton: AssembledDevice = assemble_device(automata, {'Button': checked_button})
    assert type(assembled_smartbutton.external) == CheckedDevice

    # test macro traces
    check_traces(assembled_smartbutton.external.nfa, shelley_device.test_macro['ok'],
                 shelley_device.test_macro['fail'])  # macro

    # test micro traces
    check_traces(assembled_smartbutton.internal, shelley_device.test_micro['ok'],
                 shelley_device.test_micro['fail'])  # micro


def test_desklamp():
    dev = shelley2automata(get_shelley_device('desklamp'))
    known_devices = {'Led': assemble_device(shelley2automata(get_shelley_device('led')), {}).external,
                     'Button': assemble_device(shelley2automata(get_shelley_device('button')), {}).external,
                     'Timer': assemble_device(shelley2automata(get_shelley_device('timer')), {}).external}
    assert type(assemble_device(dev, known_devices).external) == CheckedDevice
