import pytest
from pathlib import Path
from shelley.ast.visitors.pprint import PrettyPrintVisitor
from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage
from shelley.ast.devices import Device
from shelley.parsers.yaml import yaml2lark
from lark.visitors import VisitError
from shelley.shelley2automata import shelley2automata
from shelley.automata import Device as AutomataDevice
from karakuri.regular import Char, Concat, Union, Star, Nil

WORKDIR_PATH = Path() / Path(__file__).parent / "workdir"

lark_desklamp: str = """
    DeskLamp(
        ledA: Led,
        ledB: Led,
        b: Button,
        t: Timer) {    

        initial final level1 -> standby1, level2 {
            b.pressed; b.released; ledA.on; t.started;
        }

        final level2 -> standby2 {
            b.pressed; b.released;
            { t.canceled; ledB.on; } + { ledB.on; t.canceled;}
            t.started;
        }

        final standby1 -> level1 {
            t.timeout; ledA.off;
        }

        final standby2 -> level1 {
            { b.pressed; b.released; t.canceled; }
            +
            { t.timeout; }

            { ledB.off; ledA.off; }
            +
            { ledA.off; ledB.off; }
        } 

    }
    """

shelley_ast_desklamp = """Device DeskLamp uses Led, Button, Timer:
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
    standby2: (b.pressed; b.released; t.canceled;) xor (t.timeout;) (ledB.off; ledA.off;) xor (ledA.off; ledB.off;)"""

lark_led = """
base Led {

  initial final on -> off;

  final off -> on;
}
    """

shelley_ast_led = """Device Led:
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

lark_timer = """
    base Timer {

      initial final started -> canceled, timeout;

      final canceled -> started;
      
      final timeout -> started;
    }
        """

shelley_ast_timer = """Device Timer:
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


def test_led() -> None:
    """
    Test that Led (in Lark) is equivalent to Led (Shelley AST representation)
    """
    tree = lark_parser.parse(lark_led)
    shelley_device = ShelleyLanguage().transform(tree)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == shelley_ast_led


def test_timer() -> None:
    """
    Test that Timer (in Lark) is equivalent to Timer (Shelley AST representation)
    """
    tree = lark_parser.parse(lark_timer)
    shelley_device = ShelleyLanguage().transform(tree)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    assert visitor.result.strip() == shelley_ast_timer


def test_desklamp() -> None:
    """
    Test that Desklamp (in Lark) is equivalent to Desklamp (Shelley AST representation)
    """
    tree = lark_parser.parse(lark_desklamp)
    shelley_device = ShelleyLanguage().transform(tree)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == shelley_ast_desklamp


def test_clickbutton_variation() -> None:
    """
    Test that Desklamp (in Lark) is equivalent to Desklamp (Shelley AST representation)
    """

    source = """
    ClickButtonVariation (B: Button, T: Timer) {
     initial final single -> single, double {
      B.press; T.begin; {T.timeout; B.release; } + {B.release; T.timeout; }
     }
     initial final double -> single, double {
      B.press; 
      T.begin; 
      B.release; 
      {B.press; T.timeout; B.release; } + {B.press; B.release; T.end; } + {T.end; }
      {B.press;} # Note: this becomes a Char when converted to Regex
     }
    }"""

    expected = """Device ClickButtonVariation uses Button, Timer:
  events:
    single, double
  start events:
    single, double
  final events:
    single, double
  behaviours:
    single -> single
    single -> double
    double -> single
    double -> double
  subsystems:
    Button B, Timer T
  triggers:
    single: B.press; T.begin; (T.timeout; B.release;) xor (B.release; T.timeout;)
    double: B.press; T.begin; B.release; (B.press; T.timeout; B.release;) xor ((B.press; B.release; T.end;) xor (T.end;)) B.press;"""

    tree = lark_parser.parse(source)
    shelley_device = ShelleyLanguage().transform(tree)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    assert visitor.result.strip() == expected


def test_sink_operation() -> None:
    source_controller: str = """Controller (a: Valve, b: Valve, t: Timer) {
 initial level1 -> standby1 {
  a.on; t.begin; 
 }
 level2 -> standby2 {
  t.end; b.on; t.begin; 
 }
 levelX ->  {
  a.on; a.off; 
 }
 final standby1 -> level1 {
  t.out; a.off; 
 }
 final standby2 -> level1 {
  t.out; {b.off; a.off; } + {a.off; b.off; }
 }}"""

    tree = lark_parser.parse(source_controller)

    with pytest.raises(VisitError) as exc_info:
        shelley_device = ShelleyLanguage().transform(tree)

    assert (
        str(exc_info.value.orig_exc)
        == "Unusable operation levelX. Hint: Mark levelX as final or declare operations on the right side."
    )


def test_undeclared_operation_on_right_side() -> None:
    source_controller: str = """Controller (a: Valve, b: Valve, t: Timer) {
     initial level1 -> standby1, level2, levelX {
      a.on; t.begin; 
     }
     level2 -> standby2 {
      t.end; b.on; t.begin; 
     }
     final standby1 -> level1 {
      t.out; a.off; 
     }
     final standby2 -> level1 {
      t.out; {b.off; a.off; } + {a.off; b.off; }
     }

    }"""

    tree = lark_parser.parse(source_controller)

    with pytest.raises(VisitError) as exc_info:
        shelley_device = ShelleyLanguage().transform(tree)

    assert (
        str(exc_info.value.orig_exc)
        == "Operation levelX on the right side of level1 is never declared!"
    )


def test_undeclared_operation_on_right_side_base() -> None:
    source_controller: str = """base Controller  {
     initial level1 -> standby1, level2, levelX;
     level2 -> standby2;
     final standby1 -> level1;
     final standby2 -> level1;
    }"""

    tree = lark_parser.parse(source_controller)

    with pytest.raises(VisitError) as exc_info:
        shelley_device = ShelleyLanguage().transform(tree)

    assert (
        str(exc_info.value.orig_exc)
        == "Operation levelX on the right side of level1 is never declared!"
    )


def test_unusable_operation() -> None:
    """
    In this case, levelX is a sink operation but the parser doesn't detect this.
    The "Unusable operation" error will be raised in a later phase of the compilation process.
    """
    source_controller: str = """Controller (a: Valve, b: Valve, t: Timer) {
 initial level1 -> standby1, level2, levelX {
  a.on; t.begin; 
 }
 level2 -> standby2 {
  t.end; b.on; t.begin; 
 }
 levelX -> levelX {
  a.off; t.out;
 }
 final standby1 -> level1 {
  t.out; a.off; 
 }
 final standby2 -> level1 {
  t.out; {b.off; a.off; } + {a.off; b.off; }
 }

}"""

    expected_ast_controller: str = """Device Controller uses Valve, Timer:
  events:
    level1, level2, levelX, standby1, standby2
  start events:
    level1
  final events:
    standby1, standby2
  behaviours:
    level1 -> standby1
    level1 -> level2
    level1 -> levelX
    level2 -> standby2
    levelX -> levelX
    standby1 -> level1
    standby2 -> level1
  subsystems:
    Valve a, Valve b, Timer t
  triggers:
    level1: a.on; t.begin;
    level2: t.end; b.on; t.begin;
    levelX: a.off; t.out;
    standby1: t.out; a.off;
    standby2: t.out; (b.off; a.off;) xor (a.off; b.off;)"""

    tree = lark_parser.parse(source_controller)
    shelley_device = ShelleyLanguage().transform(tree)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)

    # print(visitor.result.strip())

    assert visitor.result.strip() == expected_ast_controller


def test_yaml2_lark_translation():
    """
    Test yaml2lark translation

    A.
    lark_desklamp_reference: this is the reference desklamp in Lark (see above)
    shelley_device_reference: Shelley AST representation from the lark_desklamp_reference

    B. Convert desklamp in YAML to Lark
    lark_desklamp_test: this is the desklamp in Lark obtained from the YAML translation
    shelley_device_test: Shelley AST representation from the yaml file

    C. Compare reference and test
    We use the visitor to compare both

    @return:
    """
    # A.
    lark_desklamp_reference: str = lark_parser.parse(lark_desklamp)
    shelley_device_reference: Device = ShelleyLanguage().transform(
        lark_desklamp_reference
    )

    # B.
    desklamp_yaml_path: Path = WORKDIR_PATH / "desklamp.yml"
    desklamp_lark_path: Path = WORKDIR_PATH / "desklamp.shy"
    yaml2lark.translate(desklamp_yaml_path, desklamp_lark_path)
    with open(desklamp_lark_path) as fp:
        lark_desklamp_test: str = lark_parser.parse(fp.read())
    shelley_device_test: Device = ShelleyLanguage().transform(lark_desklamp_test)

    # C.
    shelley_device_reference_visitor = PrettyPrintVisitor(
        components=shelley_device_reference.components
    )
    shelley_device_reference.accept(shelley_device_reference_visitor)

    shelley_device_test_visitor = PrettyPrintVisitor(
        components=shelley_device_test.components
    )
    shelley_device_test.accept(shelley_device_test_visitor)

    assert (
        shelley_device_reference_visitor.result.strip()
        == shelley_device_test_visitor.result.strip()
    )

    desklamp_lark_path.unlink()


def test_lot_of_subsystem_calls():
    """
    311 subsystem calls
    @return: 
    """
    source = """ValveGroup (v: Valve) {
 initial final go1 -> go1 {
  v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; 
 }
}"""

    expexted_result = """Device ValveGroup uses Valve:
  events:
    go1
  start events:
    go1
  final events:
    go1
  behaviours:
    go1 -> go1
  subsystems:
    Valve v
  triggers:
    go1: v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1; v.x1;"""

    tree = lark_parser.parse(source)
    shelley_device = ShelleyLanguage().transform(tree)

    visitor = PrettyPrintVisitor(components=shelley_device.components)
    shelley_device.accept(visitor)
    print(visitor.result.strip())
    assert visitor.result.strip() == expexted_result


def test_absent_next_option() -> None:
    fauly_led_spec = """
base Led {
 initial on -> ok, error ;
 ok -> off;
 final error -> ; # NO NEXT OPTION HERE
 final off -> off, on ;
}
"""

    tree = lark_parser.parse(fauly_led_spec)
    shelley_device = ShelleyLanguage().transform(tree)

    automata = shelley2automata(shelley_device)

    expected = AutomataDevice(
        start_events=["on"],
        final_events=["error", "off"],
        events=["on", "ok", "error", "off"],
        behavior=[
            ("on", "ok"),
            ("on", "error"),
            ("ok", "off"),
            ("error", "None"),
            ("off", "off"),
            ("off", "on"),
        ],
        components={},
        triggers={"on": Nil(), "ok": Nil(), "error": Nil(), "off": Nil()},
    )
    assert expected == automata


def test_loop() -> None:
    """
    Test that Kleene star rule mixed with other rules
    """
    lark_valvehandler: str = """
        ValveHandler(
            v1: Valve,
            v2: Valve,
            v3: Valve) {    

            initial final go -> go {
                {loop {{v1.on; v1.off;} + {v2.on; v2.off;}} v3.on; v3.off;} + {loop {v1.on; v1.off;}}
            }


        }
        """

    lark_valve = """
    base Valve {

      initial final on -> off;

      final off -> on;
    }
        """

    def pprint():
        tree = lark_parser.parse(lark_valvehandler)
        shelley_device = ShelleyLanguage().transform(tree)

        visitor = PrettyPrintVisitor(components=shelley_device.components)
        shelley_device.accept(visitor)

        # print(visitor.result.strip())

        assert (
            visitor.result.strip()
            == """Device ValveHandler uses Valve:
  events:
    go
  start events:
    go
  final events:
    go
  behaviours:
    go -> go
  subsystems:
    Valve v1, Valve v2, Valve v3
  triggers:
    go: (loop((v1.on; v1.off;) xor (v2.on; v2.off;)) v3.on; v3.off;) xor (loop(v1.on; v1.off;))"""
        )

        return shelley_device

    def shelley2nfa():

        expected = AutomataDevice(
            start_events=["go"],
            final_events=["go"],
            events=["go"],
            behavior=[("go", "go")],
            components={"v1": "Valve", "v2": "Valve", "v3": "Valve"},
            triggers={
                "go": Union(
                    left=Concat(
                        left=Concat(
                            left=Star(
                                child=Union(
                                    left=Concat(
                                        left=Char(char="v1.on"),
                                        right=Char(char="v1.off"),
                                    ),
                                    right=Concat(
                                        left=Char(char="v2.on"),
                                        right=Char(char="v2.off"),
                                    ),
                                )
                            ),
                            right=Char(char="v3.on"),
                        ),
                        right=Char(char="v3.off"),
                    ),
                    right=Star(
                        child=Concat(left=Char(char="v1.on"), right=Char(char="v1.off"))
                    ),
                )
            },
        )

        automata = shelley2automata(shelley_device)
        assert expected == automata

    shelley_device = pprint()
    shelley2nfa()
