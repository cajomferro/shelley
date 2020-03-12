from .context import shelley

from .creator import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from shelley.ast.visitors import CheckWFSyntaxVisitor
from shelley.ast.components import Component
from .creator import DDeskLamp, DTimer, DButton, DLed

declared_devices = {}

d_led = create_device_led()
declared_devices[d_led.name] = d_led

d_button = create_device_button()
declared_devices[d_button.name] = d_button

d_timer = create_device_timer()
declared_devices[d_timer.name] = d_timer

d_desk_lamp = create_device_desk_lamp(d_led, d_button, d_timer)


def test_triggers():
    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)

    for trigger_event in d_desk_lamp.triggers.keys():
        rule = d_desk_lamp.triggers[trigger_event]
        rule.accept(visitor)


def test_check_wf_syntax():
    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)
    for device in [d_desk_lamp]:
        device.accept(visitor)

    # assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)


def test_create_components():
    components = {
        Component("ledA"): DLed.name,
        Component("ledB"): DLed.name,
        Component("b"): DButton.name,
        Component("t"): DTimer.name
    }

    assert(Component("ledA") in components)
