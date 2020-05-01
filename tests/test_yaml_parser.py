import pytest
from pathlib import Path
from shelley.ast.visitors.pprint import PrettyPrintVisitor
from shelley import yaml2shelley


def _get_path(device_name: str) -> Path:
    return Path() / "tests" / "input" / "{0}.yml".format(device_name)


#
# yaml_as_dict = {
#     "device": {
#         "name": "Button",
#         "events": ["pressed", "released"],
#         "behavior": [["pressed", "released"], ["released", "pressed"]],
#     },
#     "test_macro": {
#         "ok": {
#             "valid1": [
#                 "pressed",
#                 "released",
#                 "pressed",
#                 "released",
#                 "pressed",
#                 "released",
#                 "pressed",
#                 "released",
#             ],
#             "valid2": ["pressed"],
#             "valid3": ["pressed", "released"],
#             "valid4": ["pressed", "released", "pressed"],
#             "empty": [],
#         },
#         "fail": {"invalid1": ["released", "pressed"], "invalid2": ["released"]},
#     },
# }


def test_events_invalid_event_syntax() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "events": [["pressed"], "released"],
            "behavior": [
                ["pressed", "released"],
                ["released", "pressed"],
            ],  # THIS IS WRONG
        }
    }

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        yaml2shelley._create_device_from_yaml(yaml_as_dict)

    assert (
        "Invalid syntax for event. Expecting string or dict but found ['pressed']"
        == str(exc_info.value)
    )


def test_events_start() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "events": ["pressed", "released"],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    shelley_device = yaml2shelley._create_device_from_yaml(yaml_as_dict)
    assert shelley_device.events["pressed"].is_start


def test_events_start_specified() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "events": ["pressed", {"released": {"start": True}}],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    shelley_device = yaml2shelley._create_device_from_yaml(yaml_as_dict)
    assert not shelley_device.events["pressed"].is_start
    assert shelley_device.events["released"].is_start


def test_events_no_components_but_triggers() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "events": ["pressed", {"released": {"micro": ["x.xxx"]}}],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        yaml2shelley._create_device_from_yaml(yaml_as_dict)

    assert (
        "Event 'released' specifies micro behavior but device has no components!"
        == str(exc_info.value)
    )


def test_button() -> None:
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("button"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert (
        visitor.result.strip()
        == """Device Button:
  events:
    pressed, released
  start events:
    pressed
  final events:
    pressed, released
  behaviours:
    pressed -> released
    released -> pressed
  triggers:
    pressed: fired
    released: fired"""
    )

    assert shelley_device.test_macro["ok"] == {
        "valid1": [
            "pressed",
            "released",
            "pressed",
            "released",
            "pressed",
            "released",
            "pressed",
            "released",
        ],
        "valid2": ["pressed"],
        "valid3": ["pressed", "released"],
        "valid4": ["pressed", "released", "pressed"],
        "empty": [],
    }
    assert shelley_device.test_macro["fail"] == {
        "invalid1": ["released", "pressed"],
        "invalid2": ["released"],
    }


def test_led() -> None:
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("led"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert (
        visitor.result.strip()
        == """Device Led:
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
    off: fired"""
    )


def test_timer() -> None:
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("timer"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert (
        visitor.result.strip()
        == """Device Timer:
  events:
    started, canceled, timeout
  start events:
    started
  final events:
    started, canceled, timeout
  behaviours:
    started -> canceled
    started -> timeout
    canceled -> started
    timeout -> started
  triggers:
    started: fired
    canceled: fired
    timeout: fired"""
    )


def test_sendok() -> None:
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("sendok"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert (
        visitor.result.strip()
        == """Device SendOK uses Button, Led:
  events:
    send, ok, off
  start events:
    send
  final events:
    send, ok, off
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
    )


def test_smartbutton_1() -> None:
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("smartbutton1"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert (
        visitor.result.strip()
        == """Device SmartButton uses Button:
  events:
    on
  start events:
    on
  final events:
    on
  behaviours:
    on -> on
  components:
    Button b
  triggers:
    on: ( b.pressed ; b.released )"""
    )

    assert shelley_device.test_macro["ok"] == {
        "valid1": ["on"],
        "valid2": ["on", "on", "on", "on"],
        "empty": [],
    }
    assert shelley_device.test_macro["fail"] == {"invalid1": ["off"]}

    assert shelley_device.test_micro["ok"] == {
        "valid1": ["b.pressed", "b.released"],
        "valid2": ["b.pressed", "b.released", "b.pressed", "b.released"],
        "valid3": ["b.pressed", "b.released", "b.pressed", "b.released"],
        "empty": [],
    }
    assert shelley_device.test_micro["fail"] == {
        "invalid1": ["b.released", "b.pressed"],
        "invalid2": ["b.pressed", "b.pressed"],
        "invalid3": ["b.released", "b.released"],
        "incomplete1": ["b.released"],
        "incomplete2": ["b.pressed"],
        "incomplete3": ["b.pressed", "b.released", "b.pressed"],
    }


def test_desklamp() -> None:
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("desklamp"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert (
        visitor.result.strip()
        == """Device DeskLamp uses Led, Button, Timer:
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
    level1: ( b.pressed ; ( b.released ; ( ledA.on ; t.started ) ) )
    level2: ( b.pressed ; ( b.released ; ( ( ( t.canceled ; ledB.on ) xor ( ledB.on ; t.canceled ) ) ; t.started ) ) )
    standby1: ( t.timeout ; ledA.off )
    standby2: ( ( ( b.pressed ; ( b.released ; t.canceled ) ) xor t.timeout ) ; ( ( ledB.off ; ledA.off ) xor ( ledA.off ; ledB.off ) ) )"""
    )


def test_ambiguous() -> None:
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("ambiguous"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert (
        visitor.result.strip()
        == """Device 3Buttons uses SimpleButton:
  events:
    button1AndOther, button3OrOthers
  start events:
    button1AndOther, button3OrOthers
  final events:
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
    )


def test_ambiguous_variant() -> None:
    """
    Syntax variant that uses XOR LEFT RIGHT
    """
    shelley_device = yaml2shelley.get_shelley_from_yaml(_get_path("ambiguous_variant"))
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert (
        visitor.result.strip()
        == """Device 3Buttons uses SimpleButton:
  events:
    button1AndOther, button3OrOthers, button3OrOthersv2
  start events:
    button1AndOther, button3OrOthers
  final events:
    button1AndOther, button3OrOthers, button3OrOthersv2
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
    )
