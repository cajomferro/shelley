from .context import shelley

from .creator.correct import create_device_led, create_device_button, create_device_timer, create_device_desk_lamp
from shelley.ast.visitors.wfsyntax import CheckWFSyntaxVisitor

declared_devices = {}

d_led = create_device_led()
declared_devices[d_led.name] = d_led

d_button = create_device_button()
declared_devices[d_button.name] = d_button

d_timer = create_device_timer()
declared_devices[d_timer.name] = d_timer

d_desk_lamp = create_device_desk_lamp()


def test_triggers():
    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)

    for trigger in d_desk_lamp.triggers.list():
        trigger.trigger_rule.accept(visitor)


def test_check_wf_syntax():
    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)
    for device in [d_desk_lamp]:
        device.accept(visitor)

    # assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)
