import os, pytest

from .context import appcompiler

import appcompiler
from shelley.ast import devices

EXAMPLES_PATH = 'tests/input'
COMPILED_PATH = 'tests/input/compiled'


#
# def test_find_yml():
#     with pytest.raises(CompilationError) as exc_info:
#         _find_compiled_device('examples/compiled/button.yml')
#     assert "Invalid file: examples/compiled/button.yml. Expecting extension .scy or .scb but found yml!" == str(
#         exc_info.value)
#
#     with pytest.raises(CompilationError) as exc_info:
#         _find_compiled_device('examples/compiled/button.scb')
#     assert "examples/compiled/button.scb not found! Please compile it first!" == str(exc_info.value)

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
