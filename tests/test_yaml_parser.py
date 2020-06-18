import pytest
import yaml
from pathlib import Path
from shelley.ast.visitors.pprint import PrettyPrintVisitor
from shelley.ast.devices import Device
from shelley.ast.components import Components, Component
from shelley.ast.triggers import Triggers
from shelley.ast.events import Event
from shelley import yaml2shelley
from shelley.yaml2shelley.util import MySafeLoader


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
        "invalid operation declaration: Expecting a string or a dict but found: ['pressed']"
        == str(exc_info.value)
    )


def test_events_start() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "events": [{"pressed": {"start": True}}, {"released": {"start": False}}],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    shelley_device = yaml2shelley._create_device_from_yaml(yaml_as_dict)
    assert shelley_device.events["pressed"].is_start


def test_events_start_specified() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "events": [{"pressed": {"start": False}}, {"released": {"start": True}}],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    shelley_device = yaml2shelley._create_device_from_yaml(yaml_as_dict)
    assert not shelley_device.events["pressed"].is_start
    assert shelley_device.events["released"].is_start


def test_events_from_behavior() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "behavior": [[{"pressed": {"start": True}}, {"released": {"start": False}}], ["released", "pressed"]],
        }
    }

    shelley_device = yaml2shelley._create_device_from_yaml(yaml_as_dict)
    assert shelley_device.events["pressed"].is_start
    assert shelley_device.events["pressed"].is_final
    assert not shelley_device.events["released"].is_start
    assert shelley_device.events["released"].is_final


def test_events_no_components_but_triggers() -> None:
    yaml_as_dict = {
        "device": {
            "name": "Button",
            "events": [{"pressed": {"start": True}}, {"released": {"start": False, "micro": ["x.xxx"]}}],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        yaml2shelley._create_device_from_yaml(yaml_as_dict)

    assert (
        str(exc_info.value)
        == "operation declaration error in ['released']: Only declare an integration rule when there are components (system has 0 components).\nHint: remove integration rule or declare a component."
    )


def test_auto_create_declared_event_without_micro() -> None:
    yaml_as_dict = {
        "device": {
            "name": "SmartButton",
            "components": {"b": "Button"},
            "events": [{"pressed": {"start": True}}, {"released": {"start": False, "micro": ["b.released"]}}],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        yaml2shelley._create_device_from_yaml(yaml_as_dict)

    assert (
        str(exc_info.value)
        == "operation declaration error in ['pressed']: Only declare an integration rule when there are components (system has 1 components).\nHint: write integration rule or remove all components."
    )


def test_auto_create_undeclared_event_with_micro() -> None:
    yaml_as_dict = {
        "device": {
            "name": "SmartButton",
            "components": {"b": "Button"},
            "events": [{"pressed": {"start": True}, "released": {"start": True, "micro": ["b.released"]}}],
            "behavior": [["pressed", "released"], ["released", "pressed"]],
        }
    }

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        yaml2shelley._create_device_from_yaml(yaml_as_dict)

    assert (
        str(exc_info.value)
        == "operation declaration error in ['pressed']: Only declare an integration rule when there are components (system has 1 components).\nHint: write integration rule or remove all components."
    )


def test_empty_integration() -> None:
    yaml_code = """
device:
  name: WrongButton
  behavior:
    - [on, on]
  components:
    b: SingleClickButton
  events:
    - on:
        micro: [] # ERROR: empty integration
    - off:
        micro: [ b.pressed, b.released]
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        device: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)
    assert (
        str(exc_info.value)
        == "operation declaration error in ['on']: integration rule error: An empty sequence introduces ambiguity.\nHint: remove empty sequence or add subsystem call to sequence."
    )


def test_events_triggers_different_number() -> None:
    yaml_code = """
device:
  name: WrongButton
  behavior:
    - [on, on]
  components:
    b: SingleClickButton
  events:
    - on:
        micro: [ b.pressed, b.released]
    - off:
        micro: [ b.pressed, b.released] # ERROR: off is undeclared!
    """

    with pytest.raises(yaml2shelley.ShelleyParserError) as exc_info:
        device: Device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)

    assert (
        str(exc_info.value)
        == "operation declaration error in ['off']: Every operation declaration must be referred in the behavior.\nHint: remove the definition of 'off' or add a transition with 'off' to the behavior section."
    )


def test_seq_4_options() -> None:
    e = Event("click", True, True)
    t = Triggers()
    c = Components()
    c.add(Component("B"))
    c.add(Component("T"))
    yaml_code = """
micro:
 - seq:
     - T.t
     - T.t
     - B.p
 - B.r
    """
    yaml_as_dict = yaml.load(yaml_code, MySafeLoader)
    triggers_src = yaml_as_dict["micro"]

    yaml2shelley._parse_triggers(triggers_src, e, c, t)

    visitor = PrettyPrintVisitor(components=c)
    t.accept(visitor)

    assert visitor.result.strip() == "click: T.t ; T.t ; B.p ; B.r"


def test_xor_3_options_nested() -> None:
    e = Event("click", True, True)
    t = Triggers()
    c = Components()
    c.add(Component("B"))
    c.add(Component("T"))
    yaml_code = """
micro:
 xor:
  - [B.p, T.t, B.r]
  - xor:
    - [B.p, T.e, B.r]
    - T.t
    """
    yaml_as_dict = yaml.load(yaml_code, MySafeLoader)
    triggers_src = yaml_as_dict["micro"]
    yaml2shelley._parse_triggers(triggers_src, e, c, t)

    visitor = PrettyPrintVisitor(components=c)
    t.accept(visitor)

    assert (
        visitor.result.strip()
        == "click: ( B.p ; T.t ; B.r xor ( B.p ; T.e ; B.r xor T.t ) )"
    )


def test_xor_3_options() -> None:
    e = Event("click", True, True)
    t = Triggers()
    c = Components()
    c.add(Component("B"))
    c.add(Component("T"))
    yaml_code = """
micro:
 - xor:
   - [B.p, T.t, B.r]
   - [B.p, T.e, B.r]
   - T.t
    """
    yaml_as_dict = yaml.load(yaml_code, MySafeLoader)
    triggers_src = yaml_as_dict["micro"]
    yaml2shelley._parse_triggers(triggers_src, e, c, t)

    visitor = PrettyPrintVisitor(components=c)
    t.accept(visitor)

    assert (
        visitor.result.strip()
        == "click: ( B.p ; T.t ; B.r xor B.p ; T.e ; B.r xor T.t )"
    )


def test_xor_2_options() -> None:
    e = Event("click", True, True)
    t = Triggers()
    c = Components()
    c.add(Component("B"))
    c.add(Component("T"))
    yaml_code = """
    micro:
     xor:
        - T.t
        - B.p
        """
    yaml_as_dict = yaml.load(yaml_code, MySafeLoader)
    triggers_src = yaml_as_dict["micro"]

    assert len(t) == 0
    yaml2shelley._parse_triggers(triggers_src, e, c, t)
    assert len(t) == 1

    visitor = PrettyPrintVisitor(components=c)
    t.accept(visitor)

    assert visitor.result.strip() == "click: ( T.t xor B.p )"


def test_xor_1_options() -> None:
    e = Event("click", True, True)
    t = Triggers()
    c = Components()
    c.add(Component("B"))
    c.add(Component("T"))
    yaml_code = """
    micro:
     xor:
        - T.t
        """
    yaml_as_dict = yaml.load(yaml_code, MySafeLoader)
    triggers_src = yaml_as_dict["micro"]
    yaml2shelley._parse_triggers(triggers_src, e, c, t)

    visitor = PrettyPrintVisitor(components=c)
    t.accept(visitor)
    assert visitor.result.strip() == "click: ( T.t )"


def test_xor_seq() -> None:
    e = Event("click", True, True)
    t = Triggers()
    c = Components()
    c.add(Component("b1"))
    c.add(Component("b2"))
    c.add(Component("b3"))
    yaml_code = """
micro:
    - xor:
        - xor:
            - seq:
                - b1.pressed
                - b2.pressed
            - seq:
                - b2.pressed
                - b1.pressed
        - b3.pressed
"""
    yaml_as_dict = yaml.load(yaml_code, MySafeLoader)
    triggers_src = yaml_as_dict["micro"]
    yaml2shelley._parse_triggers(triggers_src, e, c, t)

    visitor = PrettyPrintVisitor(components=c)
    t.accept(visitor)
    assert (
        visitor.result.strip()
        == "click: ( ( b1.pressed ; b2.pressed xor b2.pressed ; b1.pressed ) xor b3.pressed )"
    )


def test_xor_seq_v2() -> None:
    e = Event("click", True, True)
    t = Triggers()
    c = Components()
    c.add(Component("b1"))
    c.add(Component("b2"))
    c.add(Component("b3"))
    yaml_code = """
micro:
    - xor:
        - seq:
            - b1.pressed
            - xor:
                - b2.pressed
                - b3.pressed
        - seq:
            - xor:
                - b2.pressed
                - b3.pressed
            - b1.pressed
"""
    yaml_as_dict = yaml.load(yaml_code, MySafeLoader)
    triggers_src = yaml_as_dict["micro"]
    yaml2shelley._parse_triggers(triggers_src, e, c, t)

    visitor = PrettyPrintVisitor(components=c)
    t.accept(visitor)
    assert (
        visitor.result.strip()
        == "click: ( b1.pressed ; ( b2.pressed xor b3.pressed ) xor ( b2.pressed xor b3.pressed ) ; b1.pressed )"
    )


### INTEGRATION


def test_led() -> None:
    yaml_code = """
device:
  name: Led
  events:
  - on:
      start: true
      final: true
  - off:
      start: false
      final: true
  behavior:
    - [on, off]
    - [off, on]    
    """
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)
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
    yaml_code = """
device:
  name: Timer
  events:
    - started:
        start: True
        final: true
    - canceled:
        start: False
        final: True
    - timeout:
        start: False
        final: True
  behavior:
    - [started, canceled]
    - [started, timeout]
    - [canceled, started]
    - [timeout, started]    
    """
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)
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


def test_desklamp() -> None:
    yaml_code = """
device:
  name: DeskLamp
  components:
    ledA: Led
    ledB: Led
    b: Button
    t: Timer
  events:
    - level1:
        start: True
        micro: [b.pressed, b.released, ledA.on, t.started]
    - level2:
        micro:
          - b.pressed
          - b.released
          - xor:
              - [t.canceled, ledB.on]
              - [ledB.on, t.canceled]
          - t.started
    - standby1:
        micro: [t.timeout, ledA.off]
    - standby2:
        micro:
          - xor:
              - [b.pressed, b.released, t.canceled]
              -  t.timeout
          - xor:
                - [ledB.off, ledA.off]
                - [ledA.off, ledB.off]
  behavior:
    - [level1, standby1]
    - [level1, level2]
    - [level2, standby2]
    - [standby1, level1]
    - [standby2, level1]
    """

    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)
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
    level1: b.pressed ; b.released ; ledA.on ; t.started
    level2: b.pressed ; b.released ; ( t.canceled ; ledB.on xor ledB.on ; t.canceled ) ; t.started
    standby1: t.timeout ; ledA.off
    standby2: ( b.pressed ; b.released ; t.canceled xor t.timeout ) ; ( ledB.off ; ledA.off xor ledA.off ; ledB.off )"""
    )


def test_sendok() -> None:
    yaml_code = """
device:
  name: SendOK
  components:
    b1: Button
    b2: Button
    lgreen: Led
    lred: Led
  events:
    - send:
        start: True
        micro: [ b1.pressed, b1.released]
    - ok:
        micro:
          - xor:
              - [ lred.on, lred.off ]
              - [ lgreen.on, lgreen.off ]
    - off:
        micro: [ b2.pressed, b2.released]
  behavior:
    - [send, ok]
    - [send, off]
    - [ok, send]
    - [off, send]
        """

    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)

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
    send: b1.pressed ; b1.released
    ok: ( lred.on ; lred.off xor lgreen.on ; lgreen.off )
    off: b2.pressed ; b2.released"""
    )


def test_smartbutton() -> None:
    yaml_code = """
device:
  name: SmartButton
  components:
    b: Button
  events:
    - on:
        start: True
        final: True
        micro: [ b.pressed, b.released]
  behavior:
    - [on, on]


test_macro:
  ok:
    valid1: [on]
    valid2: [on, on, on, on]
    empty: []
  fail:
    invalid1: False

test_micro:
  ok:
    valid1: [b.pressed, b.released]
    valid2: [b.pressed, b.released, b.pressed, b.released]
    valid3: [b.pressed, b.released, b.pressed, b.released]
    empty: []
  fail:
    invalid1: [b.released, b.pressed] # wrong order
    invalid2: [b.pressed, b.pressed] # violates sequence
    invalid3: [b.released, b.released] # violates sequence
    incomplete1: [b.released] # incomplete (not a final state)
    incomplete2: [b.pressed] # incomplete (not a final state)
    incomplete3: [b.pressed, b.released, b.pressed] # incomplete (not a final state)   
    """
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)
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
    on: b.pressed ; b.released"""
    )

    assert shelley_device.test_macro["ok"] == {
        "valid1": ["on"],
        "valid2": ["on", "on", "on", "on"],
        "empty": [],
    }
    assert shelley_device.test_macro["fail"] == {"invalid1": False}

    assert shelley_device.test_micro["ok"] == {
        "valid1": ["b.pressed", "b.released"],
        "valid1": ["b.pressed", "b.released"],
        "valid2": ["b.pressed", "b.released", "b.pressed", "b.released"],
        "valid3": ["b.pressed", "b.released", "b.pressed", "b.released"],
        "empty": [],
    }

    assert shelley_device.test_micro["fail"] == {
        "invalid1": ["b.released", "b.pressed"],  # wrong order
        "invalid2": ["b.pressed", "b.pressed"],  # violates sequence
        "invalid3": ["b.released", "b.released"],  # violates sequence
        "incomplete1": ["b.released"],  # incomplete (not a final state)
        "incomplete2": ["b.pressed"],  # incomplete (not a final state)
        "incomplete3": [
            "b.pressed",
            "b.released",
            "b.pressed",
        ],  # incomplete (not a final state)
    }


def test_ambiguous_3buttons() -> None:
    yaml_code = """
device:
  name: 3Buttons
  components:
    b1: Button
    b2: Button
    b3: Button
  events:
    - button1AndOther:
        start: True
        micro:
          - xor:
              - xor:
                  - [b1.pressed, b2.pressed]
                  - [b1.pressed, b3.pressed]
              - xor:
                  - [b2.pressed, b1.pressed]
                  - [b3.pressed, b1.pressed]
    - button3OrOthers:
          start: True
          micro:
            - xor:
                - xor:
                    - seq:
                        - b1.pressed
                        - b2.pressed
                    - seq:
                        - b2.pressed
                        - b1.pressed
                - b3.pressed
  behavior:
    - [button1AndOther, button1AndOther]
    - [button1AndOther, button3OrOthers]
    - [button3OrOthers, button3OrOthers]
    - [button3OrOthers, button1AndOther]   
    """
    shelley_device = yaml2shelley.get_shelley_from_yaml_str(yaml_code)
    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert (
        visitor.result.strip()
        == """Device 3Buttons uses Button:
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
    Button b1, Button b2, Button b3
  triggers:
    button1AndOther: ( ( b1.pressed ; b2.pressed xor b1.pressed ; b3.pressed ) xor ( b2.pressed ; b1.pressed xor b3.pressed ; b1.pressed ) )
    button3OrOthers: ( ( b1.pressed ; b2.pressed xor b2.pressed ; b1.pressed ) xor b3.pressed )"""
    )
