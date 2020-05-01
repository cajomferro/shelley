import os
import pytest
from typing import Optional, Mapping, Dict
from pathlib import Path
import argparse

import shelleyc
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
    CheckedDevice,
    check_traces,
)
from shelley.ast.devices import Device as ShelleyDevice
from shelley.shelley2automata import shelley2automata
from shelley import yaml2shelley

EXAMPLES_PATH = Path() / "tests" / "input"
COMPILED_PATH = Path() / "tests" / "input" / "compiled"


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


def make_args(src_path: Path, **kwargs: Path) -> argparse.Namespace:
    assert isinstance(src_path, Path)
    uses = []
    for k, v in kwargs.items():
        uses.append(str(v) + ":" + k)
    parser = shelleyc.create_parser()
    if len(uses) > 0:
        uses = ["--uses"] + list(sorted(uses))
    return parser.parse_args(
        ["--output", get_path(src_path)] + uses + ["--device", str(src_path)]
    )


### TEST ASSEMBLE DEVICE ###


def test_assemble_button() -> None:
    shelley_device: ShelleyDevice = _get_shelley_device("button")
    automata: AutomataDevice = shelley2automata(shelley_device)

    assembled_button: AssembledDevice = AssembledDevice.make(automata, {})
    assert assembled_button.is_valid
    assert type(assembled_button.external) == CheckedDevice


def test_assemble_smart_button() -> None:
    checked_button = AssembledDevice.make(
        shelley2automata(_get_shelley_device("button")), {}
    ).external
    assert type(checked_button) == CheckedDevice

    shelley_device = _get_shelley_device("smartbutton1")
    automata = shelley2automata(shelley_device)
    assembled_smartbutton: AssembledDevice = AssembledDevice.make(
        automata, {"Button": checked_button}
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
            shelley2automata(_get_shelley_device("led")), {}
        ).external,
        "Button": AssembledDevice.make(
            shelley2automata(_get_shelley_device("button")), {}
        ).external,
        "Timer": AssembledDevice.make(
            shelley2automata(_get_shelley_device("timer")), {}
        ).external,
    }
    assembled_desklamp = AssembledDevice.make(dev, known_devices)
    assert assembled_desklamp.is_valid
    assert type(assembled_desklamp.external) == CheckedDevice


### TEST ARGPARSE ###


def test_single_device() -> None:
    device = EXAMPLES_PATH / "button.yml"
    args = make_args(device)
    assert args.device == device
    assert args.output == COMPILED_PATH / "button.scy"
    assert args.uses == []


def test_single_device_binary() -> None:
    device = EXAMPLES_PATH / "button.yml"
    parser = shelleyc.create_parser()
    args = parser.parse_args(["-b", "-d", str(device)])
    assert args.device == device
    assert args.output is None
    assert args.uses == []
    assert args.binary is True


def test_single_device_user_defined_outdir() -> None:
    device = EXAMPLES_PATH / "button.yml"
    output = EXAMPLES_PATH / "compiled" / "button.scy"
    parser = shelleyc.create_parser()
    args = make_args(device)
    assert args.device == device
    assert args.output == output
    assert args.uses == []


def test_composite_device() -> None:
    device = EXAMPLES_PATH / "desklamp.yml"
    args = make_args(
        device,
        Button=EXAMPLES_PATH / "button.scy",
        Led=EXAMPLES_PATH / "led.scy",
        Timer=EXAMPLES_PATH / "timer.scy",
    )
    assert args.device == device
    assert args.output == COMPILED_PATH / "desklamp.scy"
    assert len(args.uses) == 3
    assert args.uses[0] == mk_use(Button=EXAMPLES_PATH / "button.scy")
    assert args.uses[1] == mk_use(Led=EXAMPLES_PATH / "led.scy")
    assert args.uses[2] == mk_use(Timer=EXAMPLES_PATH / "timer.scy")


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
        shelley2automata(_get_shelley_device(name)), known_devices
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
    return shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)


def test_not_found_device() -> None:
    src_path = os.path.join(EXAMPLES_PATH, "XbuttonX.yml")
    parser = shelleyc.create_parser()
    args = parser.parse_args(["-d", src_path])

    with pytest.raises(FileNotFoundError) as exc_info:
        shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)


def test_compile_buton_ok() -> None:
    path = _compile_simple_device("button")
    assert path.exists()

    _remove_compiled_dir()


### smartbutton


def test_smartbutton_dependency_missing() -> None:
    assert not COMPILED_PATH.exists()

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)

    assert str(exc_info.value) == "Device SmartButton expects ['Button'] but found []!"

    _remove_compiled_dir()


def test_smartbutton_dependency_not_found() -> None:
    assert not COMPILED_PATH.exists()
    COMPILED_PATH.mkdir()
    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, Button=COMPILED_PATH / "button.scy")
    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)
    assert (
        str(exc_info.value)
        == "Use device not found: tests/input/compiled/button.scy. Please compile it first!"
    )

    _remove_compiled_dir()


def test_smartbutton_ok() -> None:
    # assert not COMPILED_PATH.exists()
    _compile_simple_device("button")

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, Button=COMPILED_PATH / "button.scy")

    shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found() -> None:
    COMPILED_PATH.mkdir(exist_ok=True, parents=True)

    src_path = EXAMPLES_PATH / "desklamp.yml"
    args = make_args(
        src_path,
        Button=COMPILED_PATH / "button.scy",
        Led=COMPILED_PATH / "led.scy",
        Timer=COMPILED_PATH / "timer.scy",
    )

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)
    print(exc_info.value)
    assert (
        str(exc_info.value) == "Use device not found: tests/input/compiled/button.scy. Please compile it first!"
    )

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found_2() -> None:
    # assert not COMPILED_PATH.exists()
    _compile_simple_device("button")
    # _compile_simple_device('led', COMPILED_PATH)
    _compile_simple_device("timer")

    src_path = EXAMPLES_PATH / "desklamp.yml"
    args = make_args(
        src_path,
        Button=COMPILED_PATH / "button.scy",
        Led=COMPILED_PATH / "led.scy",
        Timer=COMPILED_PATH / "timer.scy",
    )

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)

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
    args = make_args(
        src_path,
        Button=COMPILED_PATH / "button.scy",
        Led=COMPILED_PATH / "led.scy",
        Timer=COMPILED_PATH / "timer.scy",
    )
    shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)

    _remove_compiled_dir()


def test_compile_ambiguous() -> None:
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    _compile_simple_device("simple_button")

    src_path = EXAMPLES_PATH / "ambiguous.yml"
    args = make_args(src_path, SimpleButton=COMPILED_PATH / "simple_button.scy")

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        shelleyc.compile_shelley(args.device, args.uses, args.output, args.binary)

    assert "Invalid device: AmbiguityFailure" in str(exc_info.value)

    _remove_compiled_dir()
