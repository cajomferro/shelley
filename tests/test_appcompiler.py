import os
import pytest
import yaml
from pathlib import Path

from .context import shelley
from .context import appcompiler

import appcompiler
from shelley.automata import Device as AutomataDevice, AssembledDevice, assemble_device, CheckedDevice, check_traces
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley.yaml2shelley import create_device_from_yaml

EXAMPLES_PATH = Path('tests/input')
COMPILED_PATH = Path('tests/input/compiled')


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
    device = EXAMPLES_PATH / 'button.yml'
    args = make_args(device)
    assert args.device == device
    assert args.output == COMPILED_PATH / 'button.scy'
    assert args.uses == []


def test_single_device_binary():
    device = EXAMPLES_PATH / 'button.yml'
    parser = appcompiler.create_parser()
    args = parser.parse_args(['-b', '-d', str(device)])
    assert args.device == device
    assert args.output is None
    assert args.uses == []
    assert args.binary is True


def test_single_device_user_defined_outdir():
    device = EXAMPLES_PATH / 'button.yml'
    output = EXAMPLES_PATH / 'compiled' / 'button.scy'
    parser = appcompiler.create_parser()
    args = make_args(device)
    assert args.device == device
    assert args.output == output
    assert args.uses == []


def test_composite_device():
    device = EXAMPLES_PATH / 'desklamp.yml'
    args = make_args(device, Button=EXAMPLES_PATH / 'button.scy', Led=EXAMPLES_PATH / 'led.scy', Timer=EXAMPLES_PATH / 'timer.scy')
    assert args.device == device
    assert args.output == COMPILED_PATH / 'desklamp.scy'
    assert len(args.uses) == 3
    assert args.uses[0] == mk_use(Button=EXAMPLES_PATH / 'button.scy')
    assert args.uses[1] == mk_use(Led=EXAMPLES_PATH / 'led.scy')
    assert args.uses[2] == mk_use(Timer=EXAMPLES_PATH / 'timer.scy')


### TEST COMPILER ###

def _remove_compiled_dir():
    _remove_compiled_files(COMPILED_PATH)
    try:
        COMPILED_PATH.rmdir()
    except FileNotFoundError:
        pass


def _remove_compiled_files(outdir: Path = None):
    for file in outdir.glob("*.sc[y,b]"):
        file.unlink()

    """
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

    """
def _compile_simple_device(device_name, outdir: Path = None):
    src_path = EXAMPLES_PATH / (device_name + ".yml")
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    args = make_args(src_path)
    return appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)


def test_not_found_device():
    src_path = os.path.join(EXAMPLES_PATH, 'XbuttonX.yml')
    parser = appcompiler.create_parser()
    args = parser.parse_args(['-d', src_path])

    with pytest.raises(FileNotFoundError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)


def test_compile_buton_ok():
    #assert not COMPILED_PATH.exists()
    COMPILED_PATH.mkdir()
    path = _compile_simple_device('button', COMPILED_PATH)
    assert os.path.exists(path)

    _remove_compiled_dir()


### smartbutton

def get_path(p):
    assert isinstance(p, Path)
    return str(COMPILED_PATH / (p.stem + '.scy'))

def mk_use(**kwargs):
    assert len(kwargs) == 1
    for key,val in kwargs.items():
        assert isinstance(val, Path)
        assert isinstance(key, str)
        return str(val) + ":" + key

def make_args(src_path, **kwargs):
    assert isinstance(src_path, Path)
    uses = []
    for k,v in kwargs.items():
        uses.append(str(v) + ":" + k)
    parser = appcompiler.create_parser()
    if len(uses) > 0:
        uses = ['--uses'] + list(sorted(uses))
    return parser.parse_args(
        ['--output', get_path(src_path) ] + uses + ['--device', str(src_path)])

def test_smartbutton_dependency_missing():
    assert not COMPILED_PATH.exists()

    src_path = EXAMPLES_PATH / 'smartbutton1.yml'
    args = make_args(src_path)

    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)

    assert str(exc_info.value) == "Device SmartButton expects ['Button'] but found []!"

    _remove_compiled_dir()


def test_smartbutton_dependency_not_found():
    assert not COMPILED_PATH.exists()
    COMPILED_PATH.mkdir()
    src_path = EXAMPLES_PATH / 'smartbutton1.yml'
    args = make_args(src_path, Button=COMPILED_PATH/ 'button.scy')
    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)

    assert str(exc_info.value) == "Use device not found: tests/input/compiled/button.scy. Please compile it first!"

    _remove_compiled_dir()


def test_smartbutton_ok():
    #assert not COMPILED_PATH.exists()
    _compile_simple_device('button', COMPILED_PATH)

    src_path = EXAMPLES_PATH / 'smartbutton1.yml'
    args = make_args(src_path, Button=COMPILED_PATH / 'button.scy')

    appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found():
    COMPILED_PATH.mkdir(exist_ok=True, parents=True)

    src_path = EXAMPLES_PATH / 'desklamp.yml'
    args = make_args(src_path,
        Button=COMPILED_PATH/'button.scy',
        Led=COMPILED_PATH/'led.scy',
        Timer=COMPILED_PATH/'timer.scy'
    )

    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)

    assert str(exc_info.value) == "Use device not found: tests/input/compiled/button.scy. Please compile it first!"

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found_2():
    #assert not COMPILED_PATH.exists()
    _compile_simple_device('button', COMPILED_PATH)
    # _compile_simple_device('led', COMPILED_PATH)
    _compile_simple_device('timer', COMPILED_PATH)

    src_path = EXAMPLES_PATH / 'desklamp.yml'
    args = make_args(src_path,
        Button=COMPILED_PATH/'button.scy',
        Led=COMPILED_PATH/'led.scy',
        Timer=COMPILED_PATH/'timer.scy'
    )

    with pytest.raises(appcompiler.exceptions.CompilationError) as exc_info:
        appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)

    assert str(exc_info.value) == "Use device not found: tests/input/compiled/led.scy. Please compile it first!"

    _remove_compiled_dir()


def test_compile_desklamp_ok():
    #assert not COMPILED_PATH.exists()
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    _compile_simple_device('button', COMPILED_PATH)
    _compile_simple_device('led', COMPILED_PATH)
    _compile_simple_device('timer', COMPILED_PATH)

    src_path = EXAMPLES_PATH / 'desklamp.yml'
    args = make_args(src_path, Button=COMPILED_PATH/'button.scy', Led=COMPILED_PATH/'led.scy', Timer=COMPILED_PATH/'timer.scy')
    appcompiler.compile_shelley(args.device, args.uses, args.output, args.binary)

    _remove_compiled_dir()
