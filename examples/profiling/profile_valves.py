import pytest
import re
import cProfile
import timeit
from typing import List, Dict, Any
from karakuri import regular
from shelley import automata
from shelley import shelley2automata
from shelley.ast.devices import Device as ShelleyDevice
from shelley import yaml2shelley


valve_yml = """
device:
  name: Valve
  behavior:
    - [on, off]
    - [off, on]
"""

valvehandler_4valves_yml = """
device:
  name: ValveHandler
  behavior:
    - [go, go]
  components:
    v1: Valve
    v2: Valve
    v3: Valve
    v4: Valve
  events:
    - go:
        micro: [v1.on, v1.off] 
"""

valvehandler_8valves_yml = """
device:
  name: ValveHandler
  behavior:
    - [go, go]
  components:
    v1: Valve
    v2: Valve
    v3: Valve
    v4: Valve
    v5: Valve
    v6: Valve
    v7: Valve
    v8: Valve
  events:
    - go:
        micro: [v1.on, v1.off]
"""


def _get_valve_assembled() -> automata.AssembledDevice:
    valve_shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(valve_yml)
    valve_aut: automata.Device = shelley2automata.shelley2automata(valve_shy)

    return automata.AssembledDevice.make(valve_aut, {})


valve_assembled = _get_valve_assembled()


def _get_automata(yaml_code: str):

    shy: ShelleyDevice = yaml2shelley.get_shelley_from_yaml_str(yaml_code)
    aut: automata.Device = shelley2automata.shelley2automata(shy)

    return aut


# def _build_external(dev: automata.Device) -> regular.NFA:
#     automata.ensure_well_formed(dev)
#     external_behavior: regular.NFA = automata.build_external_behavior(
#         dev.behavior, dev.start_events, dev.final_events, dev.events
#     )
#
#     return external_behavior
#
#
# def _build_components(dev: automata.Device, known_devices) -> List[regular.NFA]:
#     # Since there are components, we must assemble them
#     components_behaviors: List[regular.NFA] = list(
#         dict(automata.build_components(dev.components, known_devices)).values()
#     )
#     return components_behaviors
#
#
# def _build_micro(
#     components_behaviors: List[regular.NFA[Any, str]],
#     external_behavior: regular.NFA[Any, str],
#     triggers: Dict[str, regular.Regex[str]],
# ):
#     automata.AssembledMicroBehavior.make(
#         components=components_behaviors,
#         external_behavior=external_behavior,
#         triggers=triggers,
#     )
#
#
# def _assemble(dev: automata.Device, known_devices):
#
#     external_behavior: regular.NFA = _build_external(dev)
#
#     components_behaviors: List[regular.NFA] = _build_components(dev, known_devices)
#
#     _build_micro(components_behaviors, external_behavior, dev.triggers)


def run(yaml_code) -> None:
    automata.AssembledDevice.make(
        _get_automata(yaml_code), {"Valve": valve_assembled.external}
    )


if __name__ == "__main__":
    run(valvehandler_8valves_yml)
