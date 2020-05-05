import pytest
import re
from shelley.automata import (
    Device as AutomataDevice,
    AssembledDevice,
    CheckedDevice,
    check_traces,
)
from shelley import shelley2automata
from shelley.ast.devices import Device as ShelleyDevice
from shelley import yaml2shelley


simple_yml = """
device:
  name: Simple
  behavior:
    - [on, off]
    - [off, on]
"""

composition_yml = """
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


def _get_simple_assembled() -> AssembledDevice:
    simple_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(simple_yml)
    simple_aut: AutomataDevice = shelley2automata.shelley2automata(simple_shy)

    return AssembledDevice.make(simple_aut, {})


simple_assembled = _get_simple_assembled()

# TODO: this test should raise a shelleyc error!
def test_bad() -> None:
    """
    If the device has components and event is undeclared, it means it doesn't have micro hence is invalid
    :return:
    """

    # with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
    # # introduce bad syntax on good yml
    # regex = (
    #     r"    - send:\n"
    #     r"        micro:\n"
    #     r"          xor:\n"
    #     r"            - hc.get\n"
    #     r"            - hc.post"
    # )
    # replace = r""  # send will be auto discovered without specifying micro
    # composition_yml_bad = re.sub(regex, replace, composition_yml)

    # parse yaml and assemble device
    known_devices = {"Simple": simple_assembled.external}
    composition_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
        composition_yml
    )
    composition_aut: AutomataDevice = shelley2automata.shelley2automata(composition_shy)

    composition_assembled = AssembledDevice.make(composition_aut, known_devices)

    assert composition_assembled.is_valid
    assert type(composition_assembled.external) == CheckedDevice

    # test macro traces
    check_traces(composition_assembled.external_model_check, composition_shy.test_macro)

    # test micro traces
    check_traces(composition_assembled.internal_model_check, composition_shy.test_micro)

    # assert (
    #     "Event 'send' doesn't specify micro behavior but device has components!"
    #     == str(exc_info.value)
    # )
