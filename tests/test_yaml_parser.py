import yaml
from shelley.ast.visitors.pprint import PrettyPrintVisitor
from shelley.yaml_parser import create_device_from_yaml


def test_button():
    with open('input/button.yaml', 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)

    shelley_device = create_device_from_yaml(yaml_code)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == """Device Button:
  external events:
    begin, pressed, released
  behaviours:
    begin -> pressed
    pressed -> released
    released -> pressed
  triggers:
    begin: fired
    pressed: fired
    released: fired"""


def test_led():
    with open('input/led.yaml', 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)

    shelley_device = create_device_from_yaml(yaml_code)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == """Device Led:
  external events:
    begin, on, off
  behaviours:
    begin -> on
    on -> off
    off -> on
  triggers:
    begin: fired
    on: fired
    off: fired"""


def test_timer():
    with open('input/timer.yaml', 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)

    shelley_device = create_device_from_yaml(yaml_code)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == """Device Timer:
  external events:
    begin, started, canceled, timeout
  behaviours:
    begin -> started
    started -> canceled
    started -> timeout
    canceled -> started
    timeout -> started
  triggers:
    begin: fired
    started: fired
    canceled: fired
    timeout: fired"""


def test_sendok():
    with open('input/sendok.yaml', 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley_device = create_device_from_yaml(yaml_code)
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == """Device SendOK uses Button, Led:
  external events:
    begin, send, ok, off
  behaviours:
    begin -> send
    send -> ok
    send -> off
    ok -> send
    off -> send
  components:
    Button b1, Button b2, Led lgreen, Led lred
  triggers:
    send: ( b1.pressed  ; b1.released )
    ok: ( ( lred.on  ; lred.off ) xor ( lgreen.on  ; lgreen.off ))
    off: ( b2.pressed  ; b2.released )"""


def test_desklamp():
    with open('input/desklamp.yaml', 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    shelley_device = create_device_from_yaml(yaml_code)
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == """Device DeskLamp uses Led, Button, Timer:
  external events:
    begin, level1, standby1, level2, standby2
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
    level1: ( b.pressed  ; ( b.released  ; ( ledA.on  ; t.started )))
    level2: ( ( b.pressed  ; b.released ) ; ( ( ( t.canceled  ; ledB.on ) xor ( ledB.on  ; t.canceled )) ; t.started ))
    standby1: ( t.timeout  ; ledA.off )
    standby2: ( ( ( b.pressed  ; ( b.released  ; t.canceled )) xor t.timeout ) ; ( ( ledB.off  ; ledA.off ) xor ( ledA.off  ; ledB.off )))"""
