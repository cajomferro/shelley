from typing import Dict
from shelley import yaml2shelley
from shelley.ast.devices import Device
from shelley.ast.visitors.pprint import PrettyPrintVisitor

yaml_led = """device:
  name: Led
  events:
    on:
      start: true
      final: true
      next: [off]
    off:
      start: false
      final: true
      next: [on]
"""

yaml_button = """device:
  name: Button
  events:
    pressed:
      start: true
      final: true
      next: [released]
    released:
      start: false
      final: true
      next: [pressed]
"""

yaml_timer = """device:
  name: Timer
  events:
    started:
        start: True
        final: False
        next: [canceled, timeout]
    canceled:
        start: False
        final: True
        next: [started]
    timeout:
        start: False
        final: True
        next: [started]
"""

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
        next: [standby1, level2]
    level2:
        start: False
        next: [standby2]
        micro:
          - b.pressed
          - b.released
          - xor:
              - [t.canceled, ledB.on]
              - [ledB.on, t.canceled]
          - t.started
    standby1:
        next: [level1]
        start: false
        micro: [t.timeout, ledA.off]
    standby2:
        next: [level1]
        start: false
        micro:
          - xor:
              - [b.pressed, b.released, t.canceled]
              -  t.timeout
          - xor:
                - [ledB.off, ledA.off]
                - [ledA.off, ledB.off]
"""


def test_pprint_led() -> None:
    visitor = PrettyPrintVisitor()
    yaml2shelley.get_shelley_from_yaml_str(yaml_led).accept(visitor)
    expected_str = """Device Led:
  events:
    on, off
  start events:
    on
  final events:
    on, off
  behaviours:
    on -> off
    off -> on
  triggers:
    on: fired
    off: fired

"""
    print(visitor.result)
    assert (
        visitor.result == expected_str
    )  # this can be wrong because Set doesn't guarantee elements ordering


def test_pprint_button() -> None:
    visitor = PrettyPrintVisitor()
    yaml2shelley.get_shelley_from_yaml_str(yaml_button).accept(visitor)
    print(visitor.result)


def test_pprint_timer() -> None:
    visitor = PrettyPrintVisitor()
    yaml2shelley.get_shelley_from_yaml_str(yaml_timer).accept(visitor)
    print(visitor.result)


def test_pprint_desklamp() -> None:
    declared_devices: Dict[str, Device] = {}

    d_led: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_led)
    declared_devices[d_led.name] = d_led

    d_button: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_button)
    declared_devices[d_button.name] = d_button

    d_timer: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_timer)
    declared_devices[d_timer.name] = d_timer

    d_desk_lamp: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_desklamp)

    visitor = PrettyPrintVisitor(components=d_desk_lamp.components)
    d_desk_lamp.accept(visitor)
    print(visitor.result)

    expected_str = """Device DeskLamp uses Led, Button, Timer:
  events:
    level1, level2, standby1, standby2
  start events:
    level1
  final events:
    level1, level2, standby1, standby2
  behaviours:
    level1 -> standby1
    level1 -> level2
    level2 -> standby2
    standby1 -> level1
    standby2 -> level1
  components:
    Led ledA, Led ledB, Button b, Timer t
  triggers:
    level1: b.pressed ; b.released ; ledA.on ; t.started
    level2: b.pressed ; b.released ; ( t.canceled ; ledB.on xor ledB.on ; t.canceled ) ; t.started
    standby1: t.timeout ; ledA.off
    standby2: ( b.pressed ; b.released ; t.canceled xor t.timeout ) ; ( ledB.off ; ledA.off xor ledA.off ; ledB.off )

"""

    assert (
        visitor.result == expected_str
    )  # this can be wrong because Set doesn't guarantee elements ordering
