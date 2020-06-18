import pytest
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
    CheckedDevice,
    check_traces,
)
from shelley import shelley2automata
from shelley.ast.devices import Device as ShelleyDevice
from shelley import yaml2shelley
from shelley.shelleyc import DeviceMapping


simple_yml: str = """
device:
  name: Simple
  events:
  - on:
      start: true
      final: true
  - off:
      start: false
      final: true
  behavior:
    - [on, off]
    - [off, on]
"""

composition_yml_src: str = """
device:
  name: Composition
  components:
    s: Simple
  events:
    - go:
        start: True
        micro: [s.on]
    - stop:
        start: False
        micro: [s.off]
    - bad:
        start: True
        micro: [s.badbadbad] # WRONG! DOESN'T EXIST IN MICRO!
  behavior:
    - [go, stop]
    - [stop, go]
    - [bad, bad]


"""

composition_yml_tests = """
test_macro:
  ok:
    valid1: [go, stop]
    valid2: [go, stop, go, stop]
    valid3: [go, stop, go]
    valid4: [go]
    validbad: [bad, bad, bad, bad]
  fail:
    invalid1: [stop]
    invalid2: [stop, go]    
    invalid3: [go, bad]    

test_micro:
  ok:
    valid1: [s.on, s.off]
    valid2: [s.on, s.off, s.on, s.off]
    valid3: [s.on]
    validbad: [s.badbadbad] # THIS IS WRONG!!!
  fail:
    invalid1: [s.off]
    invalid2: [s.off, s.on]
"""

composition_yml = composition_yml_src + composition_yml_tests


def _get_simple_assembled() -> AssembledDevice:
    simple_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(simple_yml)
    simple_aut: AutomataDevice = shelley2automata.shelley2automata(simple_shy)

    return AssembledDevice.make(simple_aut, DeviceMapping(dict(), False).__getitem__)


simple_assembled = _get_simple_assembled()


def test_bad_tests() -> None:
    """
    If the device has components and event is undeclared, it means it doesn't have micro hence is invalid
    :return:
    """

    with pytest.raises(ValueError) as exc_info:

        # parse yaml and assemble device
        known_devices = {"Simple": simple_assembled.external}
        composition_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            composition_yml
        )
        composition_aut: AutomataDevice = shelley2automata.shelley2automata(
            composition_shy
        )

        composition_assembled = AssembledDevice.make(
            composition_aut, known_devices.__getitem__
        )

        assert composition_assembled.is_valid
        assert type(composition_assembled.external) == CheckedDevice

        # test macro traces
        check_traces(
            composition_assembled.external_model_check, composition_shy.test_macro
        )

        # test micro traces
        check_traces(
            composition_assembled.internal_model_check, composition_shy.test_micro
        )

    assert "Operation 'bad': unknown operations {'s.badbadbad'}" == str(exc_info.value)


# TODO: this test should raise a shelleyc error!
def test_bad() -> None:
    """
    If the device has components and event is undeclared, it means it doesn't have micro hence is invalid
    :return:
    """

    with pytest.raises(ValueError) as exc_info:

        # parse yaml and assemble device
        known_devices = {"Simple": simple_assembled.external}
        composition_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            composition_yml_src
        )
        composition_aut: AutomataDevice = shelley2automata.shelley2automata(
            composition_shy
        )

        composition_assembled = AssembledDevice.make(
            composition_aut, known_devices.__getitem__
        )

        assert composition_assembled.is_valid
        assert type(composition_assembled.external) == CheckedDevice

        # test macro traces
        check_traces(
            composition_assembled.external_model_check, composition_shy.test_macro
        )

        # test micro traces
        check_traces(
            composition_assembled.internal_model_check, composition_shy.test_micro
        )

    assert "Operation 'bad': unknown operations {'s.badbadbad'}" == str(exc_info.value)
