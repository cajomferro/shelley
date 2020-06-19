from typing import Dict
from shelley import yaml2shelley
from shelley.ast.devices import Device
from shelley.ast.visitors.wfsyntax import CheckWFSyntaxVisitor

yaml_led = """device:
  name: Led
  events:
    on:
      start: true
      final: true
    off:
      start: false
      final: true
  behavior:
    - [on, off]
    - [off, on]"""

yaml_button = """device:
  name: Button
  events:
    pressed:
      start: true
      final: true
    released:
      start: false
      final: true
  behavior:
    - [pressed, released]
    - [released, pressed]"""

yaml_timer = """device:
  name: Timer
  events:
    started:
        start: True
        final: False
    canceled:
        start: False
        final: True
    timeout:
        start: False
        final: True
  behavior:
    - [started, canceled]
    - [started, timeout]
    - [canceled, started]
    - [timeout, started]"""

yaml_desklamp = """device:
  name: DeskLamp
  components:
    ledA: Led
    ledB: Led
    b: Button
    t: Timer
  events:
    level1:
        start: True
        micro: [b.pressed, b.released, ledA.on, t.started]
    level2:
        micro:
          - b.pressed
          - b.released
          - xor:
              - [t.canceled, ledB.on]
              - [ledB.on, t.canceled]
          - t.started
    standby1:
        micro: [t.timeout, ledA.off]
    standby2:
        micro:
          - xor:
              - [b.pressed, b.released, t.canceled]
              -  t.timeout
          - xor:
                - [ledB.off, ledA.off]
                - [ledA.off, ledB.off]
  behavior:
    - [level1, standby1]
    - [level1, level2]
    - [level2, standby2]
    - [standby1, level1]
    - [standby2, level1]"""


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
