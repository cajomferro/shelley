from typing import Dict
from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage
from shelley.ast.devices import Device
from shelley.ast.visitors.pprint import PrettyPrintVisitor

source_led = """
base Led {
 initial final on -> off;
 final off -> on;
}
"""

source_button = """
base Button {
 initial final pressed -> released;
 final released -> pressed;
}
"""

source_timer = """
base Timer {
 initial started -> canceled, timeout;
 final canceled -> started;
 final timeout -> started;
}
"""

source_desklamp = """
DeskLamp(ledA: Led, ledB: Led, b: Button, t: Timer) {
 initial final level1 -> standby1, level2 {
  b.pressed; b.released; ledA.on; t.started; 
 }
 final level2 -> standby2 {
  b.pressed; b.released; {t.canceled; ledB.on; } + {ledB.on; t.canceled; }t.started; 
 }
 final standby1 -> level1 {
  t.timeout; ledA.off; 
 }
 final standby2 -> level1 {
  {b.pressed; b.released; t.canceled; } + {t.timeout; }{ledB.off; ledA.off; } + {ledA.off; ledB.off; }
 }
}
"""


def test_pprint_led() -> None:
    visitor = PrettyPrintVisitor()
    ShelleyLanguage().transform(lark_parser.parse(source_led)).accept(visitor)
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
    ShelleyLanguage().transform(lark_parser.parse(source_button)).accept(visitor)
    print(visitor.result)


def test_pprint_timer() -> None:
    visitor = PrettyPrintVisitor()
    ShelleyLanguage().transform(lark_parser.parse(source_timer)).accept(visitor)
    print(visitor.result)


def test_pprint_desklamp() -> None:
    declared_devices: Dict[str, Device] = {}

    d_led: Device = ShelleyLanguage().transform(lark_parser.parse(source_led))
    declared_devices[d_led.name] = d_led

    d_button: Device = ShelleyLanguage().transform(lark_parser.parse(source_button))
    declared_devices[d_button.name] = d_button

    d_timer: Device = ShelleyLanguage().transform(lark_parser.parse(source_timer))
    declared_devices[d_timer.name] = d_timer

    d_desk_lamp: Device = ShelleyLanguage().transform(
        lark_parser.parse(source_desklamp)
    )

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
  subsystems:
    Led ledA, Led ledB, Button b, Timer t
  triggers:
    level1: b.pressed; b.released; ledA.on; t.started;
    level2: b.pressed; b.released; (t.canceled; ledB.on;) xor (ledB.on; t.canceled;) t.started;
    standby1: t.timeout; ledA.off;
    standby2: (b.pressed; b.released; t.canceled;) xor (t.timeout;) (ledB.off; ledA.off;) xor (ledA.off; ledB.off;)

"""

    assert (
        visitor.result == expected_str
    )  # this can be wrong because Set doesn't guarantee elements ordering
