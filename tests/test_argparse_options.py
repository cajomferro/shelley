import yaml
from pathlib import Path
import argparse
from shelley.shelleyc import shelleyc
from shelley.shelleyc import main
from typing import Optional

EXAMPLES_PATH = Path()
COMPILED_PATH = EXAMPLES_PATH / "compiled"


def get_path(p: Path) -> str:
    assert isinstance(p, Path)
    return str(COMPILED_PATH / (p.stem + ".scy"))


def make_args(src_path: Path, uses_path: Optional[Path] = None) -> argparse.Namespace:

    parser = main.create_parser()
    args: argparse.Namespace

    if uses_path is not None:
        assert isinstance(uses_path, Path)

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


def test_single_device() -> None:
    device = EXAMPLES_PATH / "button.yml"
    args = make_args(device)
    assert args.device == device
    assert args.output == COMPILED_PATH / "button.scy"
    assert args.uses == None


def test_no_output() -> None:
    devicepath: Path = EXAMPLES_PATH / "button.yml"
    outpath: Path = EXAMPLES_PATH / "button.scy"
    parser = main.create_parser()
    args: argparse.Namespace = parser.parse_args(
        ["-d", str(devicepath), "-o", str(outpath), "--no-output"]
    )
    assert args.device == devicepath
    assert args.output == outpath
    assert args.uses == None
    assert args.save_output == False


def test_single_device_binary() -> None:
    device = EXAMPLES_PATH / "button.yml"
    parser = main.create_parser()
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

    uses_yaml = {
        "Button": "tests/input/compiled/button.scy",
        "SimpleButton": "tests/input/compiled/simple_button.scy",
        "Led": "tests/input/compiled/led.scy",
        "Timer": "tests/input/compiled/timer.scy",
    }

    with args.uses.open(mode="w") as f:
        yaml.dump(uses_yaml, f)

    assert shelleyc._parse_uses(args.uses) == uses_yaml

    uses.unlink()
