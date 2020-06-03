import os
import pytest
from typing import Optional, Mapping
from pathlib import Path
import argparse

from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
    CheckedDevice,
    check_traces,
)
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley import yaml2shelley, shelleyc
from shelley.shelleyc import parser as shelleyc_parser

EXAMPLES_PATH = Path() / "tests" / "input"
COMPILED_PATH = Path() / "tests" / "input" / "compiled"


def empty_devices(name: str) -> CheckedDevice:
    raise ValueError()


def _remove_compiled_dir() -> None:
    _remove_compiled_files(COMPILED_PATH)
    try:
        COMPILED_PATH.rmdir()
    except FileNotFoundError:
        pass


def _remove_compiled_files(outdir: Path) -> None:
    for file in outdir.glob("*.sc[y,b]"):
        file.unlink()


def _get_shelley_device(name: str) -> ShelleyDevice:
    path = (
        Path.cwd()
        / EXAMPLES_PATH
        / "{name}.{ext}".format(
            name=name, ext=shelleyc.settings.EXT_SHELLEY_SOURCE_YAML[0]
        )
    )
    return yaml2shelley.get_shelley_from_yaml(path)


def _get_compiled_path(name: str, binary: bool = False) -> Path:
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    if binary:
        ext = shelleyc.settings.EXT_SHELLEY_COMPILED_BIN  # scb
    else:
        ext = shelleyc.settings.EXT_SHELLEY_COMPILED_YAML  # scy
    return Path.cwd() / COMPILED_PATH / "{0}.{1}".format(name, ext)


def get_path(p: Path) -> str:
    assert isinstance(p, Path)
    return str(COMPILED_PATH / (p.stem + ".scy"))


def mk_use(**kwargs: Path) -> str:
    assert len(kwargs) == 1
    for key, val in kwargs.items():
        assert isinstance(val, Path)
        assert isinstance(key, str)
        return str(val) + ":" + key
    raise ValueError()


def make_args(src_path: Path, uses_path: Optional[Path] = None) -> argparse.Namespace:
    assert isinstance(src_path, Path) and src_path.exists()

    parser = shelleyc_parser.create_parser()
    args: argparse.Namespace

    if uses_path is not None:
        assert isinstance(uses_path, Path) and uses_path.exists()

        args = parser.parse_args(
            ["--output", get_path(src_path)]
            + ["--uses", str(uses_path)]
            + ["--device", str(src_path)]
        )
    else:
        args = parser.parse_args(
            ["--output", get_path(src_path)] + ["--device", str(src_path)]
        )

    return args


yaml_button = """device:
  name: Button
  events: [pressed,released]
  behavior:
    - [pressed, released]
    - [released, pressed]

test_macro:
  ok:
    valid1: [pressed, released, pressed, released, pressed, released, pressed, released]
    valid2: [pressed]
    valid3: [pressed, released]
    valid4: [pressed, released, pressed]
    empty: []
  fail:
    invalid1: [released, pressed]
    invalid2: [released]"""

### TEST ASSEMBLE DEVICE ###


def test_assemble_button() -> None:
    shelley_device: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(yaml_button)
    automata: AutomataDevice = shelley2automata(shelley_device)

    assembled_button: AssembledDevice = AssembledDevice.make(automata, empty_devices)
    assert assembled_button.is_valid
    assert type(assembled_button.external) == CheckedDevice


def test_assemble_smart_button() -> None:
    checked_button = AssembledDevice.make(
        yaml2shelley.get_shelley_from_yaml_str(yaml_button), empty_devices
    ).external
    assert type(checked_button) == CheckedDevice

    shelley_device = _get_shelley_device("smartbutton1")
    automata = shelley2automata(shelley_device)
    assembled_smartbutton: AssembledDevice = AssembledDevice.make(
        automata, {"Button": checked_button}.__getitem__
    )
    assert assembled_smartbutton.is_valid
    assert type(assembled_smartbutton.external) == CheckedDevice

    with pytest.raises(ValueError) as exc_info:
        # test micro traces
        check_traces(
            assembled_smartbutton.internal_model_check,
            {"ok": {"good": ["b.released", "b.pressed"]}, "fail": {}},
        )  # micro

    assert (
        str(exc_info.value)
        == "Unaccepted valid trace 'good': ['b.released', 'b.pressed']"
    )


def test_assemble_desklamp() -> None:
    dev = shelley2automata(_get_shelley_device("desklamp"))
    known_devices = {
        "Led": AssembledDevice.make(
            shelley2automata(_get_shelley_device("led")), empty_devices
        ).external,
        "Button": AssembledDevice.make(
            yaml2shelley.get_shelley_from_yaml_str(yaml_button), empty_devices
        ).external,
        "Timer": AssembledDevice.make(
            shelley2automata(_get_shelley_device("timer")), empty_devices
        ).external,
    }
    assembled_desklamp = AssembledDevice.make(dev, known_devices.__getitem__)
    assert assembled_desklamp.is_valid
    assert type(assembled_desklamp.external) == CheckedDevice


### TEST ARGPARSE ###


def test_single_device() -> None:
    device = EXAMPLES_PATH / "button.yml"
    args = make_args(device)
    assert args.device == device
    assert args.output == COMPILED_PATH / "button.scy"
    assert args.uses == None


def test_no_output() -> None:
    devicepath: Path = EXAMPLES_PATH / "button.yml"
    outpath: Path = EXAMPLES_PATH / "button.scy"
    parser = shelleyc_parser.create_parser()
    args: argparse.Namespace = parser.parse_args(
        ["-d", str(devicepath), "-o", str(outpath), "--no-output"]
    )
    assert args.device == devicepath
    assert args.output == outpath
    assert args.uses == None
    assert args.save_output == False


def test_single_device_binary() -> None:
    device = EXAMPLES_PATH / "button.yml"
    parser = shelleyc_parser.create_parser()
    args = parser.parse_args(["-b", "-d", str(device)])
    assert args.device == device
    assert args.output is None
    assert args.uses == None
    assert args.binary is True


def test_single_device_user_defined_outdir() -> None:
    device = EXAMPLES_PATH / "button.yml"
    output = EXAMPLES_PATH / "compiled" / "button.scy"
    args = make_args(device)
    assert args.device == device
    assert args.output == output
    assert args.uses == None


def test_composite_device() -> None:
    device = EXAMPLES_PATH / "desklamp.yml"
    uses = EXAMPLES_PATH / "uses.yml"

    args = make_args(device, uses)

    assert args.device == device
    assert args.output == COMPILED_PATH / "desklamp.scy"
    assert args.uses == uses

    assert shelleyc_parser.parse_uses(args.uses) == {
        "Button": "tests/input/compiled/button.scy",
        "SimpleButton": "tests/input/compiled/simple_button.scy",
        "Led": "tests/input/compiled/led.scy",
        "Timer": "tests/input/compiled/timer.scy",
    }


### TEST SERIALIZER ###


def _serialize(
    name: str,
    known_devices: Optional[Mapping[str, CheckedDevice]] = None,
    binary: bool = False,
) -> CheckedDevice:
    if known_devices is None:
        known_devices = {}
    path = _get_compiled_path(name, binary=binary)
    assembled_device: AssembledDevice = AssembledDevice.make(
        shelley2automata(_get_shelley_device(name)), known_devices.__getitem__
    )
    shelleyc.serializer.serialize(
        path, assembled_device.external.nfa.as_dict(flatten=False), binary
    )
    return assembled_device.external


def _test_serializer_button(binary: bool = False) -> None:
    name = "button"

    # serialize and deserialize (yaml)
    path = _get_compiled_path(name, binary=binary)
    checked_device = _serialize(name, binary=binary)
    deserialized_device = shelleyc.serializer.deserialize(path, binary)

    assert deserialized_device == checked_device


def _test_serializer_smartbutton1(binary: bool = False) -> None:
    # serialize and deserialize button

    _serialize("button", binary=binary)
    button_path = _get_compiled_path("button", binary=binary)

    button_device = shelleyc.serializer.deserialize(button_path, binary)

    known_devices = {"Button": button_device}

    # serialize and deserialize smartbutton
    path = _get_compiled_path("smartbutton1", binary=binary)
    checked_device = _serialize("smartbutton1", known_devices, binary=binary)
    deserialized_device = shelleyc.serializer.deserialize(path, binary)

    assert deserialized_device == checked_device


def test_serializer_button() -> None:
    _test_serializer_button(binary=False)
    _remove_compiled_files(COMPILED_PATH)


def test_serializer_button_binary() -> None:
    _test_serializer_button(binary=True)
    _remove_compiled_files(COMPILED_PATH)


def test_serializer_smartbutton1() -> None:
    _test_serializer_smartbutton1(binary=False)
    _remove_compiled_files(COMPILED_PATH)


def test_serializer_smartbutton1_binary() -> None:
    _test_serializer_smartbutton1(binary=True)
    _remove_compiled_files(COMPILED_PATH)


### TEST COMPILER ###


def _compile_simple_device(device_name: str) -> Path:
    src_path = EXAMPLES_PATH / (device_name + ".yml")
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    args = make_args(src_path)
    return shelleyc.compile_shelley(
        args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
    )


def test_not_found_device() -> None:
    src_path = os.path.join(EXAMPLES_PATH, "XbuttonX.yml")
    parser = shelleyc_parser.create_parser()
    args = parser.parse_args(["-d", src_path])

    with pytest.raises(FileNotFoundError) as exc_info:
        shelleyc.compile_shelley(
            args.device, args.uses, dst_path=args.output, binary=args.binary
        )


def test_compile_buton_ok() -> None:
    path = _compile_simple_device("button")
    assert path.exists()

    _remove_compiled_dir()


def test_compile_buton_no_output() -> None:
    src_path: Path = EXAMPLES_PATH / "button.yml"
    outpath: Path = COMPILED_PATH / "button.scy"
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    assert src_path.exists()
    assert not outpath.exists()
    parser = shelleyc_parser.create_parser()
    args: argparse.Namespace = parser.parse_args(
        ["-d", str(src_path), "-o", str(outpath), "--no-output"]
    )
    shelleyc.compile_shelley(
        args.device,
        shelleyc_parser.parse_uses(args.uses),
        dst_path=args.output,
        binary=args.binary,
        skip_checks=args.skip_checks,
    )
    assert src_path.exists()
    assert not outpath.exists()
    _remove_compiled_dir()


### smartbutton


def test_smartbutton_file_invalid_dict_uses_file() -> None:
    assert not COMPILED_PATH.exists()
    uses_path = EXAMPLES_PATH / "invalid_uses4.yml"

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(
            args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
        )

    assert (
        str(exc_info.value)
        == "Shelley parser error: uses file must be a valid dictionary"
    )

    _remove_compiled_dir()


def test_smartbutton_file_not_found_uses_file() -> None:
    assert not COMPILED_PATH.exists()
    uses_path = EXAMPLES_PATH / "invalid_uses3.yml"

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(
            args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
        )

    assert (
        str(exc_info.value)
        == "Use device not found: buttonBAD.scy. Please compile it first!"
    )

    _remove_compiled_dir()


def test_smartbutton_not_in_uses_file() -> None:
    assert not COMPILED_PATH.exists()
    uses_path = EXAMPLES_PATH / "invalid_uses2.yml"

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(
            args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
        )

    assert str(exc_info.value) == "Error loading system 'Button': system not defined"

    _remove_compiled_dir()


def test_smartbutton_empty_uses_file() -> None:
    assert not COMPILED_PATH.exists()
    uses_path = EXAMPLES_PATH / "invalid_uses.yml"

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(
            args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
        )

    assert str(exc_info.value) == "Error loading system 'Button': system not defined"

    _remove_compiled_dir()


def test_smartbutton_ok() -> None:
    # assert not COMPILED_PATH.exists()
    _compile_simple_device("button")

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    uses_path = EXAMPLES_PATH / "uses.yml"

    args = make_args(src_path, uses_path)

    shelleyc.compile_shelley(
        args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
    )

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found() -> None:
    COMPILED_PATH.mkdir(exist_ok=True, parents=True)

    src_path = EXAMPLES_PATH / "desklamp.yml"
    uses_path = EXAMPLES_PATH / "invalid_uses.yml"

    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(
            args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
        )

    assert str(exc_info.value) == "Error loading system 'Led': system not defined"

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found_2() -> None:
    # assert not COMPILED_PATH.exists()
    _compile_simple_device("button")
    # _compile_simple_device('led', COMPILED_PATH) --> THIS IS NOT TO BE COMPILED ON PURPOSE
    _compile_simple_device("timer")

    src_path = EXAMPLES_PATH / "desklamp.yml"
    uses_path = EXAMPLES_PATH / "uses.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(
            args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
        )

    assert (
        str(exc_info.value)
        == "Use device not found: tests/input/compiled/led.scy. Please compile it first!"
    )

    _remove_compiled_dir()


def test_compile_desklamp_ok() -> None:
    # assert not COMPILED_PATH.exists()
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    _compile_simple_device("button")
    _compile_simple_device("led")
    _compile_simple_device("timer")

    src_path = EXAMPLES_PATH / "desklamp.yml"
    uses_path = EXAMPLES_PATH / "uses.yml"
    args = make_args(src_path, uses_path)

    shelleyc.compile_shelley(
        args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
    )

    _remove_compiled_dir()


def test_compile_ambiguous() -> None:
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    _compile_simple_device("simple_button")

    src_path = EXAMPLES_PATH / "ambiguous.yml"
    uses_path = EXAMPLES_PATH / "uses.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(
            args.device, shelleyc_parser.parse_uses(args.uses), args.output, args.binary
        )

    assert "Invalid device: AmbiguityFailure" in str(exc_info.value)

    _remove_compiled_dir()
