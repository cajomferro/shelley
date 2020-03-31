import yaml
import os
import sys

from .context import shelley

from karakuri import regular

from . import settings

from shelley.automata import Device as AutomataDevice, check_valid_device, CheckedDevice, InvalidBehavior
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml
from shelley.compiler import _deserialize_checked_device, _serialize_checked_device


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    with open('tests/input/{0}.yaml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley2automata(shelley)


def main():
    try:
        os.mkdir(settings.COMPILED_FILES_DIR)
    except FileExistsError:
        pass

    settings.DEVICE_PATH = os.path.realpath(sys.argv[1])
    settings.DEVICE_NAME = os.path.splitext(os.path.basename(settings.DEVICE_PATH))[0]
    print(settings.DEVICE_PATH)
    print(settings.DEVICE_NAME)

    path = os.path.join(os.path.realpath(settings.COMPILED_FILES_DIR), '{0}.pickle'.format(settings.DEVICE_NAME))
    checked_device = check_valid_device(_get_automata_from_yaml(settings.DEVICE_NAME), {})
    assert type(checked_device) == CheckedDevice

    _serialize_checked_device(path, checked_device)
    # assert os.path.exists(path)

    deserialized_device = _deserialize_checked_device(path)

    #    os.remove(path)
    #    assert os.path.exists(path) is False

    dfa_checked_device = regular.nfa_to_dfa(checked_device.nfa)
    dfa_deserialized_device = regular.nfa_to_dfa(deserialized_device.nfa)

    # assert dfa_deserialized_device.is_equivalent_to(dfa_checked_device)


if __name__ == "__main__":
    main()
