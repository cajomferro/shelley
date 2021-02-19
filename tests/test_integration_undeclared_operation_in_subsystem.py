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
from shelley.automata.errors import UNDECLARED_OPERATION_IN_SUBSYSTEM

simple_yml: str = """
name: Simple
start_with: [on]
end_with: $ANY
operations:
    on:
      next: [off]
    off:
      next: [on]
"""

bad_composition_yml_src: str = """
name: Composition
start_with: [go, bad]
end_with: $ANY
components:
    s: Simple
operations:
    go:
        micro: [s.on]
        next: [stop]
    stop:
        micro: [s.off]
        next: [go]
    bad:
        micro: [s.badbad, s.badbadbad] # WRONG! UNDECLARED OPERATION IN THE SUBSYSTEM!
        next: [bad]
"""

good_composition_yml_src: str = """
name: Composition
start_with: [go]
end_with: $ANY
components:
    s: Simple
operations:
    go:
        micro: [s.on]
        next: [stop]
    stop:
        micro: [s.off]
        next: [go]
"""


def _get_simple_assembled() -> AssembledDevice:
    simple_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(simple_yml)
    simple_aut: AutomataDevice = shelley2automata.shelley2automata(simple_shy)
    return AssembledDevice.make(simple_aut, DeviceMapping().__getitem__)


simple_assembled = _get_simple_assembled()


def test_undeclared_operation_in_subsystem() -> None:
    """
    If a system has declared subsystems and an operation is undeclared, it means it doesn't have a valid integration
    :return:
    """

    with pytest.raises(ValueError) as exc_info:
        # parse yaml and assemble device
        known_devices = {"Simple": simple_assembled.external}
        composition_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
            bad_composition_yml_src
        )
        composition_aut: AutomataDevice = shelley2automata.shelley2automata(
            composition_shy
        )

        # this raises error
        composition_assembled = AssembledDevice.make(
            composition_aut, known_devices.__getitem__
        )

    assert UNDECLARED_OPERATION_IN_SUBSYSTEM("bad", {"s.badbad", "s.badbadbad"}) == str(
        exc_info.value
    )


# def test_unknown_integration_operation_bad_tests() -> None:
#     """
#     If a system has declared subsystems and an operation is undeclared, it means it doesn't have a valid integration
#     :return:
#     """
#
#     with pytest.raises(ValueError) as exc_info:
#
#         # parse yaml and assemble device
#         known_devices = {"Simple": simple_assembled.external}
#         composition_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(
#             good_composition_yml_bad_tests
#         )
#         composition_aut: AutomataDevice = shelley2automata.shelley2automata(
#             composition_shy
#         )
#
#         composition_assembled = AssembledDevice.make(
#             composition_aut, known_devices.__getitem__
#         )
#
#         assert composition_assembled.is_valid
#         assert type(composition_assembled.external) == CheckedDevice
#
#         # test macro traces
#         check_traces(
#             composition_assembled.external_model_check, composition_shy.test_macro
#         )
#
#         # test micro traces
#         check_traces(
#             composition_assembled.internal_model_check, composition_shy.test_micro
#         )
#
#     assert "Operation 'bad': unknown operations {'s.badbadbad'}" == str(exc_info.value)
