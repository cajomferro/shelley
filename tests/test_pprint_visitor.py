from .context import shelley

from .creator.correct import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from shelley.ast.visitors import PrettyPrintVisitor

declared_devices = {}

d_led = create_device_led()
declared_devices[d_led.name] = d_led

d_button = create_device_button()
declared_devices[d_button.name] = d_button

d_timer = create_device_timer()
declared_devices[d_timer.name] = d_timer

d_desk_lamp = create_device_desk_lamp(d_led, d_button, d_timer)


def test_pprint_led():
    visitor = PrettyPrintVisitor()
    d_led.accept(visitor)
    expected_str = \
        """\nDevice LED:
  actions:
    turnOn, turnOff, 
  internal events:
    on, off, 
  external events:
    begin, 
  behaviours:
    begin -> on
    on -> off
    off -> on
"""
    assert (visitor.result == expected_str)


def test_pprint_button():
    visitor = PrettyPrintVisitor()
    d_button.accept(visitor)


def test_pprint_timer():
    visitor = PrettyPrintVisitor()
    d_timer.accept(visitor)


def test_pprint_desklamp():
    visitor = PrettyPrintVisitor(components=d_desk_lamp.components, declared_devices=declared_devices)
    d_desk_lamp.accept(visitor)
    print(visitor.result)

    # assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)
