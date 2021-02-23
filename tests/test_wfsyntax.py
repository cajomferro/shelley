from typing import Dict
from shelley import yaml2shelley
from shelley.ast.devices import Device
from shelley.ast.visitors.wfsyntax import CheckWFSyntaxVisitor

yaml_led = """
  name: Led
  start_with: [on]
  end_with: $ANY
  operations:
    on:
      next: [off]
    off:
      next: [on]
    """

yaml_button = """
  name: Button
  start_with: [pressed]
  end_with: $ANY
  operations:
    pressed:
      next: [released]
    released:
      next: [pressed]
    """

yaml_timer = """
  name: Timer
  start_with: [started]
  end_with: $ANY
  operations:
    started:
        next: [canceled, timeout]
    canceled:
        next: [started]
    timeout:
        next: [started]
    """

yaml_desklamp = """
  name: DeskLamp
  start_with: [level1]
  end_with: $ANY
  subsystems:
    ledA: Led
    ledB: Led
    b: Button
    t: Timer
  operations:
    level1:
        requires: [b.pressed, b.released, ledA.on, t.started]
        next: [standby1, level2]
    level2:
        next: [standby2]
        requires:
          - b.pressed
          - b.released
          - xor:
              - [t.canceled, ledB.on]
              - [ledB.on, t.canceled]
          - t.started
    standby1:
        next: [level1]
        requires: [t.timeout, ledA.off]
    standby2:
        next: [level1]
        requires:
          - xor:
              - [b.pressed, b.released, t.canceled]
              -  t.timeout
          - xor:
                - [ledB.off, ledA.off]
                - [ledA.off, ledB.off]
    """


def test_triggers() -> None:
    declared_devices: Dict[str, Device] = {}

    d_led: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_led)
    declared_devices[d_led.name] = d_led

    d_button: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_button)
    declared_devices[d_button.name] = d_button

    d_timer: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_timer)
    declared_devices[d_timer.name] = d_timer

    d_desk_lamp: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_desklamp)

    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)

    for trigger in d_desk_lamp.triggers.list():
        trigger.trigger_rule.accept(visitor)


def test_check_wf_syntax() -> None:
    declared_devices: Dict[str, Device] = {}

    d_led: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_led)
    declared_devices[d_led.name] = d_led

    d_button: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_button)
    declared_devices[d_button.name] = d_button

    d_timer: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_timer)
    declared_devices[d_timer.name] = d_timer

    d_desk_lamp: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_desklamp)

    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)
    for device in [d_desk_lamp]:
        device.accept(visitor)

    # assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)
