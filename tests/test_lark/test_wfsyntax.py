from typing import Dict
from shelley.ast.devices import Device
from shelley.ast.visitors.wfsyntax import CheckWFSyntaxVisitor
from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage

source_led = """
base Led {
 initial final on -> off ;
 final off -> on ;
}"""

source_button = """
base Button {
 initial final pressed -> released ;
 final released -> pressed ;
}"""

source_timer = """
base Timer {
 initial final started -> canceled, timeout ;
 final canceled -> started ;
 final timeout -> started ;
}"""

source_desklamp = """
DeskLamp (ledA: Led, ledB: Led, b: Button, t: Timer) {
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
}"""


def test_triggers() -> None:
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

    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)

    for trigger in d_desk_lamp.triggers.list():
        trigger.trigger_rule.accept(visitor)


def test_check_wf_syntax() -> None:
    declared_devices: Dict[str, Device] = {}

    d_led: Device = ShelleyLanguage().transform(lark_parser.parse(source_led))
    declared_devices[d_led.name] = d_led

    d_button: Device = ShelleyLanguage().transform(lark_parser.parse(source_button))
    declared_devices[d_button.name] = d_button

    d_timer: Device = ShelleyLanguage().transform(lark_parser.parse(source_timer))
    declared_devices[d_timer.name] = d_timer

    d_desk_lamp: Device = ShelleyLanguage().transform(lark_parser.parse(source_led))

    visitor = CheckWFSyntaxVisitor(d_desk_lamp, declared_devices)
    for device in [d_desk_lamp]:
        device.accept(visitor)

    # assertEqual("((b.released  xor (ledA.on  xor t.canceled )) ; ledB.on )", visitor.rule)
