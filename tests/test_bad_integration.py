import pytest
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
)
from pathlib import Path
from shelley import shelley2automata
from shelley.ast.devices import Device as ShelleyDevice
from shelley.parsers import shelley_lark_parser
from shelley.shelleyc import shelleyc

EXAMPLES_PATH = Path() / Path(__file__).parent.parent / "shelley-examples"

# bad_integration_v1
BUTTON_PATH = EXAMPLES_PATH / "base" / "button.shy"
SMARTBUTTON_PATH = EXAMPLES_PATH / "bad_integration_v1" / "smartbutton.shy"

# bad_integration_v2
TIMER_PATH = EXAMPLES_PATH / "base" / "timer.shy"
CLICKBUTTON_PATH = EXAMPLES_PATH / "bad_integration_v2" / "clickbutton.shy"

# bad_integration_v3
LED_PATH = EXAMPLES_PATH / "base" / "led_strict.shy"
SIMPLE_BUTTON_PATH = EXAMPLES_PATH / "base" / "simple_button.shy"
LEDBUTTON_PATH = EXAMPLES_PATH / "bad_integration_v3" / "ledbutton.shy"


def _get_assembled_device(path: Path) -> AssembledDevice:
    simple_shy: ShelleyDevice = shelley_lark_parser.parse(path)
    simple_aut: AutomataDevice = shelley2automata.shelley2automata(simple_shy)
    return AssembledDevice.make(simple_aut, shelleyc.DeviceMapping().__getitem__)


button_assembled = _get_assembled_device(BUTTON_PATH)
timer_assembled = _get_assembled_device(TIMER_PATH)
led_assembled = _get_assembled_device(LED_PATH)
simple_button_assembled = _get_assembled_device(SIMPLE_BUTTON_PATH)


def test_bad_integration_v1() -> None:
    """
    Smartbutton uses Button improperly.
    """

    assert button_assembled.is_valid

    # parse yaml and assemble device
    known_devices = {"Button": button_assembled.external}
    composition_shy: ShelleyDevice = shelley_lark_parser.parse(SMARTBUTTON_PATH)
    composition_aut: AutomataDevice = shelley2automata.shelley2automata(composition_shy)

    composition_assembled = AssembledDevice.make(
        composition_aut, known_devices.__getitem__
    )

    assert not composition_assembled.is_valid

    # we might get 2 possible errors depending on the system generated trace

    err = """integration error

* system: on
* integration: b.press, b.press
                        ^^^^^^^
Instance errors:

  'b': press, press
              ^^^^^
"""

    err2 = """integration error

* system: on, on
* integration: b.press, b.press
                        ^^^^^^^
Instance errors:

  'b': press, press
              ^^^^^
"""

    assert (
        str(composition_assembled.failure) == err
        or str(composition_assembled.failure) == err2
    )


def test_bad_integration_v2() -> None:
    """
    Clickbutton uses Button improperly.
    """

    assert button_assembled.is_valid
    assert timer_assembled.is_valid

    # parse yaml and assemble device
    known_devices = {
        "Button": button_assembled.external,
        "Timer": timer_assembled.external,
    }
    composition_shy: ShelleyDevice = shelley_lark_parser.parse(CLICKBUTTON_PATH)
    composition_aut: AutomataDevice = shelley2automata.shelley2automata(composition_shy)

    composition_assembled = AssembledDevice.make(
        composition_aut, known_devices.__getitem__
    )

    assert not composition_assembled.is_valid

    # we might get 2 possible errors depending on the system generated trace

    err = """integration error

* system: single
* integration: B.press, T.start, B.release, T.start
                                            ^^^^^^^
Instance errors:

  'T': start, start
              ^^^^^
"""

    assert (
        str(composition_assembled.failure) == err
    )  # or str(composition_assembled.failure) == err2


def test_bad_integration_v3() -> None:
    """
    LedButton uses Led improperly.
    """

    assert simple_button_assembled.is_valid
    assert led_assembled.is_valid

    # parse yaml and assemble device
    known_devices = {
        "Button": button_assembled.external,
        "Timer": timer_assembled.external,
    }
    composition_shy: ShelleyDevice = shelley_lark_parser.parse(CLICKBUTTON_PATH)
    composition_aut: AutomataDevice = shelley2automata.shelley2automata(composition_shy)

    composition_assembled = AssembledDevice.make(
        composition_aut, known_devices.__getitem__
    )

    assert not composition_assembled.is_valid

    # we might get 2 possible errors depending on the system generated trace

    err = """integration error

* system: single
* integration: B.press, T.start, B.release, T.start
                                            ^^^^^^^
Instance errors:

  'T': start, start
              ^^^^^
"""

    assert (
        str(composition_assembled.failure) == err
    )  # or str(composition_assembled.failure) == err2
