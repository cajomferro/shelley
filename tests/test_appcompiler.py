import os
import pytest
import yaml

from .context import shelley
from .context import appcompiler

import appcompiler
from shelley.automata import Device as AutomataDevice, AssembledDevice, assemble_device, CheckedDevice, check_traces
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml

EXAMPLES_PATH = 'tests/input'
COMPILED_PATH = 'tests/input/compiled'


### TEST ASSEMBLE DEVICE ###

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


### TEST ARGPARSE ###

def test_single_device():
    device = os.path.join(EXAMPLES_PATH, 'button.yml')
    parser = appcompiler.create_parser()
    args = parser.parse_args(['-d', device])
    assert args.device == device
    assert args.outdir is None
    assert args.uses == []


def test_single_device_binary():
    device = os.path.join(EXAMPLES_PATH, 'button.yml')
    parser = appcompiler.create_parser()
    args = parser.parse_args(['-b', '-d', device])
    assert args.device == device
    assert args.outdir is None
    assert args.uses == []
    assert args.binary is True


def test_single_device_user_defined_outdir():
    device = os.path.join(EXAMPLES_PATH, 'button.yml')
    outdir = os.path.join(EXAMPLES_PATH, 'compiled')
    parser = appcompiler.create_parser()
    args = parser.parse_args(['--device', device, '--outdir', outdir])
    assert args.device == device
    assert args.outdir == outdir
    assert args.uses == []


def test_composite_device():
    device = os.path.join(EXAMPLES_PATH, 'desklamp.yml')
    outdir = 'compiled/'
    uses_button = '{0}:Button'.format(os.path.join(EXAMPLES_PATH, 'button.scy'))
    uses_led = '{0}:Led'.format(os.path.join(EXAMPLES_PATH, 'led.scy'))
    uses_timer = '{0}:Timer'.format(os.path.join(EXAMPLES_PATH, 'timer.scy'))
    parser = appcompiler.create_parser()
    args = parser.parse_args(['--outdir', outdir, '--uses', uses_button, uses_led, uses_timer, '--device', device])
    assert args.device == device
    assert args.outdir == outdir
    assert len(args.uses) == 3
    assert args.uses[0] == uses_button
    assert args.uses[1] == uses_led
    assert args.uses[2] == uses_timer


### TEST COMPILER ###

def _remove_compiled_dir():
    _remove_compiled_files(COMPILED_PATH)
    os.rmdir(COMPILED_PATH)


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


def _compile_simple_device(device_name, outdir: str = None):
    src_path = os.path.join(EXAMPLES_PATH, '{0}.yml'.format(device_name))
    parser = appcompiler.create_parser()
    args = parser.parse_args(['-o', outdir, '-d', src_path])

    return appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)


def test_not_found_device():
    src_path = os.path.join(EXAMPLES_PATH, 'XbuttonX.yml')
    parser = appcompiler.create_parser()
    args = parser.parse_args(['-d', src_path])

    with pytest.raises(FileNotFoundError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)


def test_compile_buton_ok():
    assert not os.path.exists(COMPILED_PATH)

    path = _compile_simple_device('button', COMPILED_PATH)
    assert os.path.exists(path)

    _remove_compiled_dir()


### smartbutton

def test_smartbutton_dependency_missing():
    assert not os.path.exists(COMPILED_PATH)

    src_path = os.path.join(EXAMPLES_PATH, 'smartbutton1.yml')
    parser = appcompiler.create_parser()
    args = parser.parse_args(
        ['--outdir', COMPILED_PATH, '--device', src_path])

    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)

    assert str(exc_info.value) == "Device SmartButton expects ['Button'] but found []!"

    _remove_compiled_dir()


def test_smartbutton_dependency_not_found():
    assert not os.path.exists(COMPILED_PATH)

    src_path = os.path.join(EXAMPLES_PATH, 'smartbutton1.yml')
    uses_button = '{0}:Button'.format(os.path.join(COMPILED_PATH, 'button.scy'))
    parser = appcompiler.create_parser()
    args = parser.parse_args(
        ['--outdir', COMPILED_PATH, '--uses', uses_button, '--device', src_path])

    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)

    assert str(exc_info.value) == "Use device not found: tests/input/compiled/button.scy. Please compile it first!"

    _remove_compiled_dir()


def test_smartbutton_ok():
    assert not os.path.exists(COMPILED_PATH)

    _compile_simple_device('button', COMPILED_PATH)

    src_path = os.path.join(EXAMPLES_PATH, 'smartbutton1.yml')
    uses_button = '{0}:Button'.format(os.path.join(COMPILED_PATH, 'button.scy'))
    parser = appcompiler.create_parser()
    args = parser.parse_args(
        ['--outdir', COMPILED_PATH, '--uses', uses_button, '--device', src_path])

    appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found():
    assert not os.path.exists(COMPILED_PATH)

    src_path = os.path.join(EXAMPLES_PATH, 'desklamp.yml')
    uses_button = '{0}:Button'.format(os.path.join(COMPILED_PATH, 'button.scy'))
    uses_led = '{0}:Led'.format(os.path.join(COMPILED_PATH, 'led.scy'))
    uses_timer = '{0}:Timer'.format(os.path.join(COMPILED_PATH, 'timer.scy'))
    parser = appcompiler.create_parser()
    args = parser.parse_args(
        ['--outdir', COMPILED_PATH, '--uses', uses_button, uses_led, uses_timer, '--device', src_path])

    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)

    assert str(exc_info.value) == "Use device not found: tests/input/compiled/button.scy. Please compile it first!"

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found_2():
    assert not os.path.exists(COMPILED_PATH)

    _compile_simple_device('button', COMPILED_PATH)
    # _compile_simple_device('led', COMPILED_PATH)
    _compile_simple_device('timer', COMPILED_PATH)

    src_path = os.path.join(EXAMPLES_PATH, 'desklamp.yml')
    uses_button = '{0}:Button'.format(os.path.join(COMPILED_PATH, 'button.scy'))
    uses_led = '{0}:Led'.format(os.path.join(COMPILED_PATH, 'led.scy'))
    uses_timer = '{0}:Timer'.format(os.path.join(COMPILED_PATH, 'timer.scy'))
    parser = appcompiler.create_parser()
    args = parser.parse_args(
        ['--outdir', COMPILED_PATH, '--uses', uses_button, uses_led, uses_timer, '--device', src_path])

    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)

    assert str(exc_info.value) == "Use device not found: tests/input/compiled/led.scy. Please compile it first!"

    _remove_compiled_dir()


def test_compile_desklamp_ok():
    assert not os.path.exists(COMPILED_PATH)

    _compile_simple_device('button', COMPILED_PATH)
    _compile_simple_device('led', COMPILED_PATH)
    _compile_simple_device('timer', COMPILED_PATH)

    src_path = os.path.join(EXAMPLES_PATH, 'desklamp.yml')
    uses_button = '{0}:Button'.format(os.path.join(COMPILED_PATH, 'button.scy'))
    uses_led = '{0}:Led'.format(os.path.join(COMPILED_PATH, 'led.scy'))
    uses_timer = '{0}:Timer'.format(os.path.join(COMPILED_PATH, 'timer.scy'))
    parser = appcompiler.create_parser()
    args = parser.parse_args(
        ['--outdir', COMPILED_PATH, '--uses', uses_button, uses_led, uses_timer, '--device', src_path])

    appcompiler.compile_shelley(args.device, args.uses, args.outdir, args.binary)

    _remove_compiled_dir()
