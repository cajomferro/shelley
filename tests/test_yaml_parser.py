import yaml
from .context import shelley
from shelley.ast.devices import Device
from shelley.ast.visitors.pprint import PrettyPrintVisitor
from shelley.yaml2shelley import create_device_from_yaml


def get_shelley_device(name: str) -> Device:
    with open('examples/test_yaml_parser/{0}.yml'.format(name), 'r') as stream:
        yaml_code = yaml.load(stream, Loader=yaml.BaseLoader)
    return create_device_from_yaml(yaml_code)


def test_button():
    shelley_device = get_shelley_device('button')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == """Device Button:
  external events:
    pressed, released
  start events:
    pressed
  behaviours:
    pressed -> released
    released -> pressed
  triggers:
    pressed: fired
    released: fired"""


def test_led():
    shelley_device = get_shelley_device('led')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == """Device Led:
  external events:
    on, off
  start events:
    on
  behaviours:
    on -> off
    off -> on
  triggers:
    on: fired
    off: fired"""


def test_timer():
    shelley_device = get_shelley_device('timer')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == """Device Timer:
  external events:
    started, canceled, timeout
  start events:
    started
  behaviours:
    started -> canceled
    started -> timeout
    canceled -> started
    timeout -> started
  triggers:
    started: fired
    canceled: fired
    timeout: fired"""


def test_sendok():
    shelley_device = get_shelley_device('sendok')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == """Device SendOK uses Button, Led:
  external events:
    send, ok, off
  start events:
    send
  behaviours:
    send -> ok
    send -> off
    ok -> send
    off -> send
  components:
    Button b1, Button b2, Led lgreen, Led lred
  triggers:
    send: ( b1.pressed ; b1.released )
    ok: ( ( lred.on ; lred.off ) xor ( lgreen.on ; lgreen.off ) )
    off: ( b2.pressed ; b2.released )"""


def test_smartbutton_1():
    shelley_device = get_shelley_device('smartbutton1')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == """Device SmartButton uses Button:
  external events:
    on
  start events:
    on
  behaviours:
    on -> on
  components:
    Button b
  triggers:
    on: ( b.pressed ; b.released )"""


def test_desklamp():
    shelley_device = get_shelley_device('desklamp')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == """Device DeskLamp uses Led, Button, Timer:
  external events:
    level1, standby1, level2, standby2
  start events:
    level1
  behaviours:
    level1 -> standby1
    level1 -> level2
    level2 -> standby2
    standby1 -> level1
    standby2 -> level1
  components:
    Led ledA, Led ledB, Button b, Timer t
  triggers:
    level1: ( b.pressed ; ( b.released ; ( ledA.on ; t.started ) ) )
    level2: ( b.pressed ; ( b.released ; ( ( ( t.canceled ; ledB.on ) xor ( ledB.on ; t.canceled ) ) ; t.started ) ) )
    standby1: ( t.timeout ; ledA.off )
    standby2: ( ( ( b.pressed ; ( b.released ; t.canceled ) ) xor t.timeout ) ; ( ( ledB.off ; ledA.off ) xor ( ledA.off ; ledB.off ) ) )"""


def test_3buttons():
    shelley_device = get_shelley_device('3buttons')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == """Device 3Buttons uses SimpleButton:
  external events:
    button1AndOther, button3OrOthers
  start events:
    button1AndOther, button3OrOthers
  behaviours:
    button1AndOther -> button1AndOther
    button1AndOther -> button3OrOthers
    button3OrOthers -> button3OrOthers
    button3OrOthers -> button1AndOther
  components:
    SimpleButton b1, SimpleButton b2, SimpleButton b3
  triggers:
    button1AndOther: ( ( ( b1.pressed ; b2.pressed ) xor ( b1.pressed ; b3.pressed ) ) xor ( ( b2.pressed ; b1.pressed ) xor ( b3.pressed ; b1.pressed ) ) )
    button3OrOthers: ( ( ( b1.pressed ; b2.pressed ) xor ( b2.pressed ; b1.pressed ) ) xor b3.pressed )"""


def test_3buttons_variant():
    """
    Syntax variant that uses XOR LEFT RIGHT
    """
    shelley_device = get_shelley_device('3buttons_variant')
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == """Device 3Buttons uses SimpleButton:
  external events:
    button1AndOther, button3OrOthersv2, button3OrOthers
  start events:
    button1AndOther, button3OrOthers
  behaviours:
    button1AndOther -> button3OrOthersv2
    button1AndOther -> button1AndOther
    button1AndOther -> button3OrOthers
    button3OrOthers -> button3OrOthers
    button3OrOthers -> button1AndOther
  components:
    SimpleButton b1, SimpleButton b2, SimpleButton b3
  triggers:
    button1AndOther: ( ( b1.pressed ; ( b2.pressed xor b3.pressed ) ) xor ( ( b2.pressed xor b3.pressed ) ; b1.pressed ) )
    button3OrOthers: ( ( ( b1.pressed ; b2.pressed ) xor ( b2.pressed ; b1.pressed ) ) xor b3.pressed )
    button3OrOthersv2: ( ( ( b1.pressed ; b2.pressed ) xor ( b2.pressed ; b1.pressed ) ) xor b3.pressed )"""
