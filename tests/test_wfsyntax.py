from typing import Dict
from pathlib import Path
from shelley import yaml2shelley
from shelley.ast.devices import Device
from shelley.ast.visitors.wfsyntax import CheckWFSyntaxVisitor


def _get_path(device_name: str) -> Path:
    return Path() / "tests" / "input" / "{0}.yml".format(device_name)


def test_triggers() -> None:
    declared_devices: Dict[str, Device] = {}

    d_led: Device = yaml2shelley.get_shelley_from_yaml(_get_path("led"))
    declared_devices[d_led.name] = d_led

    d_button: Device = yaml2shelley.get_shelley_from_yaml(_get_path("button"))
    declared_devices[d_button.name] = d_button

    d_timer: Device = yaml2shelley.get_shelley_from_yaml(_get_path("timer"))
    declared_devices[d_timer.name] = d_timer

    d_desk_lamp: Device = yaml2shelley.get_shelley_from_yaml(_get_path("desklamp"))

    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)

    for trigger in d_desk_lamp.triggers.list():
        trigger.trigger_rule.accept(visitor)


def test_check_wf_syntax() -> None:
    declared_devices: Dict[str, Device] = {}

    d_led: Device = yaml2shelley.get_shelley_from_yaml(_get_path("led"))
    declared_devices[d_led.name] = d_led

    d_button: Device = yaml2shelley.get_shelley_from_yaml(_get_path("button"))
    declared_devices[d_button.name] = d_button

    d_timer: Device = yaml2shelley.get_shelley_from_yaml(_get_path("timer"))
    declared_devices[d_timer.name] = d_timer

    d_desk_lamp: Device = yaml2shelley.get_shelley_from_yaml(_get_path("desklamp"))

    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)
    for device in [d_desk_lamp]:
        device.accept(visitor)

    # assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)
