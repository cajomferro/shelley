# Shelley to NFA[S,A] --> S: tipo do estado (str ou int), A: tipo do alfabeto (str)

from .context import shelley

import typing
import yaml
import os

from karakuri import regular

from shelley.automata import Device as AutomataDevice, CheckedDevice, assemble_device
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml
from appcompiler import settings, serializer

COMPILED_FILES_PATH = 'tests/input'
EXAMPLES_PATH = 'tests/input'


def _remove_compiled_files(outdir: str = None):
    if outdir is not None:
        if not os.path.exists(outdir):
            return  # compiled dir may not exist yet so skip removing files
        target_dir = outdir
    else:
        target_dir = EXAMPLES_PATH

    filtered_files = [file for file in os.listdir(target_dir) if file.endswith(".scy") or file.endswith(".scb")]
    for file in filtered_files:
        path_to_file = os.path.join(target_dir, file)
        os.remove(path_to_file)


def _get_automata_from_yaml(name: str) -> AutomataDevice:
    with open('{0}/{1}.{2}'.format(EXAMPLES_PATH, name, settings.EXT_SHELLEY_SOURCE_YAML[0]), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley: ShelleyDevice = create_device_from_yaml(yaml_code)
    return shelley2automata(shelley)


def _get_compiled_path(name: str, binary=False):
    if binary:
        ext = settings.EXT_SHELLEY_COMPILED_BIN
    else:
        ext = settings.EXT_SHELLEY_COMPILED_YAML
    try:
        os.mkdir(COMPILED_FILES_PATH)
    except FileExistsError:
        pass
    return os.path.join(os.path.realpath(COMPILED_FILES_PATH), '{0}.{1}'.format(name, ext))


def _serialize(name, known_devices=None, binary=False) -> CheckedDevice:
    if known_devices is None:
        known_devices = {}
    path = _get_compiled_path(name, binary=binary)
    checked_device: CheckedDevice = assemble_device(_get_automata_from_yaml(name), known_devices).external
    serializer.serialize(path, checked_device, binary)
    return checked_device


def _test_button(binary=False):
    name = 'button'

    # serialize and deserialize (yaml)
    path = _get_compiled_path(name, binary=binary)
    checked_device = _serialize(name, binary=binary)
    deserialized_device = serializer.deserialize(path, binary)

    assert deserialized_device == checked_device


def _test_smartbutton1(binary=False):
    # serialize and deserialize button

    _serialize('button', binary=binary)
    button_path = _get_compiled_path('button', binary=binary)

    button_device = serializer.deserialize(button_path, binary)

    known_devices = {
        'Button': button_device
    }

    # serialize and deserialize smartbutton
    path = _get_compiled_path('smartbutton1', binary=binary)
    checked_device = _serialize('smartbutton1', known_devices, binary=binary)
    deserialized_device = serializer.deserialize(path, binary)

    assert deserialized_device == checked_device


def test_button():
    _test_button(binary=False)
    _remove_compiled_files(COMPILED_FILES_PATH)


def test_button_binary():
    _test_button(binary=True)
    _remove_compiled_files(COMPILED_FILES_PATH)


def test_smartbutton1():
    _test_smartbutton1(binary=False)
    _remove_compiled_files(COMPILED_FILES_PATH)


def test_smartbutton1_binary():
    _test_smartbutton1(binary=True)
    _remove_compiled_files(COMPILED_FILES_PATH)
