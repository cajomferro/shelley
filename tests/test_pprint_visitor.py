import shelley
from typing import Dict
from shelley.ast.devices import Device
from .creator.correct import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from shelley.ast.visitors.pprint import PrettyPrintVisitor

declared_devices:Dict[str,Device]  = {}

d_led = create_device_led()
declared_devices[d_led.name] = d_led

d_button = create_device_button()
declared_devices[d_button.name] = d_button

d_timer = create_device_timer()
declared_devices[d_timer.name] = d_timer

d_desk_lamp = create_device_desk_lamp()


def test_pprint_led() -> None:
    visitor = PrettyPrintVisitor()
    d_led.accept(visitor)
    expected_str = \
        """Device Led:
  actions:
    turnOn, turnOff
  internal events:
    on, off
  external events:
    begin
  start events:
    begin
  behaviours:
    begin -> turnOn() on
    on -> turnOff() off
    off -> turnOn() on
  triggers:
    begin: fired
    on: fired
    off: fired

"""
    print(visitor.result)
    assert (visitor.result == expected_str) # this can be wrong because Set doesn't guarantee elements ordering


def test_pprint_button() -> None:
    visitor = PrettyPrintVisitor()
    d_button.accept(visitor)
    print(visitor.result)


def test_pprint_timer() -> None:
    visitor = PrettyPrintVisitor()
    d_timer.accept(visitor)
    print(visitor.result)


def test_pprint_desklamp() -> None:
    visitor = PrettyPrintVisitor(components=d_desk_lamp.components)
    d_desk_lamp.accept(visitor)
    print(visitor.result)

    expected_str = """Device DeskLamp uses Led, Button, Timer:
  external events:
    begin, level1, level2, standby1, standby2
  start events:
    begin
  behaviours:
    begin -> level1
    level1 -> standby1
    level1 -> level2
    level2 -> standby2
    standby1 -> level1
    standby2 -> level1
  components:
    Led ledA, Led ledB, Button b, Timer t
  triggers:
    begin: ( b.begin ; ( ledA.begin ; ( ledB.begin ; t.begin ) ) )
    level1: ( b.pressed ; ( b.released ; ( ledA.on ; t.started ) ) )
    level2: ( b.pressed ; ( b.released ; ( ( ( t.canceled ; ledB.on ) xor ( ledB.on ; t.canceled ) ) ; t.started ) ) )
    standby1: ( t.timeout ; ledA.off )
    standby2: ( ( ( b.pressed ; ( b.released ; t.canceled ) ) xor t.timeout ) ; ( ( ledB.off ; ledA.off ) xor ( ledA.off ; ledB.off ) ) )

"""

    assert (visitor.result == expected_str)  # this can be wrong because Set doesn't guarantee elements ordering
