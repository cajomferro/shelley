import os
import pytest
from typing import Optional, Any
from pathlib import Path
import argparse

from shelley.automata import CheckedDevice
from shelley.ast.devices import Device as ShelleyDevice
from shelley import parsers, shelleyc
from shelley.shelleyc import main

EXAMPLES_PATH = Path() / Path(__file__).parent / "input"
COMPILED_PATH = EXAMPLES_PATH / "compiled"


def empty_devices(name: str) -> CheckedDevice:
    raise ValueError()


def call_shelleyc(args: argparse.Namespace, **kwargs: Any) -> Path:
    data = dict(
        src_path=args.device,
        uses_path=args.uses,
        dst_path=args.output,
        binary=args.binary,
        skip_checks=args.skip_checks,
        save_output=args.save_output,
    )
    data.update(kwargs)
    return shelleyc.compile_shelley(**data)


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
    return parsers.get_shelley_from_yaml(path)


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

    parser = main.create_parser()
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


### TEST COMPILER ###


def _compile_simple_device(device_name: str) -> Path:
    src_path = EXAMPLES_PATH / (device_name + ".yml")
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    return call_shelleyc(make_args(src_path), save_output=True)


def test_not_found_device() -> None:
    src_path = os.path.join(EXAMPLES_PATH, "XbuttonX.yml")
    parser = main.create_parser()
    args = parser.parse_args(["-d", src_path])

    with pytest.raises(FileNotFoundError) as exc_info:
        call_shelleyc(args)


def test_compile_buton_no_output() -> None:
    src_path: Path = EXAMPLES_PATH / "button.yml"
    outpath: Path = COMPILED_PATH / "button.scy"

    assert not outpath.exists()
    parser = main.create_parser()
    args: argparse.Namespace = parser.parse_args(
        ["-d", str(src_path), "-o", str(outpath), "--no-output"]
    )
    call_shelleyc(args)
    assert not outpath.exists()


### smartbutton


def test_smartbutton_file_invalid_dict_uses_file() -> None:
    assert not COMPILED_PATH.exists()
    uses_path = EXAMPLES_PATH / "invalid_uses4.yml"

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        call_shelleyc(args)

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
        call_shelleyc(args)
    path = EXAMPLES_PATH / "buttonBAD.scy"
    assert (
            str(exc_info.value) == f"Use device not found: {path}. Please compile it first!"
    )

    _remove_compiled_dir()


def test_smartbutton_not_in_uses_file() -> None:
    assert not COMPILED_PATH.exists()
    uses_path = EXAMPLES_PATH / "invalid_uses2.yml"

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        call_shelleyc(args)

    assert str(exc_info.value) == "Error loading system 'Button': system not defined"

    _remove_compiled_dir()


def test_smartbutton_empty_uses_file() -> None:
    assert not COMPILED_PATH.exists()
    uses_path = EXAMPLES_PATH / "invalid_uses.yml"

    src_path = EXAMPLES_PATH / "smartbutton1.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        call_shelleyc(args)

    assert str(exc_info.value) == "Error loading system 'Button': system not defined"

    _remove_compiled_dir()


def test_compile_desklamp_dependency_not_found() -> None:
    COMPILED_PATH.mkdir(exist_ok=True, parents=True)

    src_path = EXAMPLES_PATH / "desklamp.yml"
    uses_path = EXAMPLES_PATH / "invalid_uses.yml"

    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        call_shelleyc(args)

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
        call_shelleyc(args)

    path = COMPILED_PATH / "led.scy"
    assert (
            str(exc_info.value) == f"Use device not found: {path}. Please compile it first!"
    )

    _remove_compiled_dir()


def test_compile_ambiguous() -> None:
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)
    _compile_simple_device("simple_button")

    src_path = EXAMPLES_PATH / "ambiguous.yml"
    uses_path = EXAMPLES_PATH / "uses.yml"
    args = make_args(src_path, uses_path)

    with pytest.raises(shelleyc.exceptions.CompilationError) as exc_info:
        call_shelleyc(args)

    assert "Invalid device: AmbiguityFailure" in str(exc_info.value)

    _remove_compiled_dir()


@pytest.fixture(scope='session', autouse=True)
def cleanup():
    _remove_compiled_dir()
