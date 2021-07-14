# Shelley to NFA[S,A] --> S: state type (str or int), A: alphabet type (str)

from karakuri.regular import Char, Concat, Union, NIL

from shelley.automata import Device as AutomataDevice
from shelley.shelley2automata import shelley2automata
from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage


def test_button() -> None:

    source = """
base Button {
 initial final pressed -> released ;
 final released -> pressed ;
}
"""

    expected = AutomataDevice(
        start_events=["pressed"],
        final_events=["pressed", "released"],
        events=["pressed", "released"],
        behavior=[("pressed", "released"), ("released", "pressed"),],
        components={},
        triggers={"pressed": NIL, "released": NIL,},
    )
    assert expected == shelley2automata(
        ShelleyLanguage().transform(lark_parser.parse(source))
    )


def test_led() -> None:

    source = """
base Led {
 initial final on -> off ;
 final off -> on ;
}
"""

    expected = AutomataDevice(
        start_events=["on"],
        final_events=["on", "off"],
        events=["on", "off"],
        behavior=[("on", "off"), ("off", "on"),],
        components={},
        triggers={"on": NIL, "off": NIL,},
    )
    assert expected == shelley2automata(
        ShelleyLanguage().transform(lark_parser.parse(source))
    )


def test_timer() -> None:

    source = """
base Timer {
 initial final started -> canceled, timeout ;
 final canceled -> started ;
 final timeout -> started ;
}
"""

    expected = AutomataDevice(
        start_events=["started"],
        final_events=["started", "canceled", "timeout"],
        events=["started", "canceled", "timeout"],
        behavior=[
            ("started", "canceled"),
            ("started", "timeout"),
            ("canceled", "started"),
            ("timeout", "started"),
        ],
        components={},
        triggers={"started": NIL, "canceled": NIL, "timeout": NIL},
    )
    assert expected == shelley2automata(
        ShelleyLanguage().transform(lark_parser.parse(source))
    )


def test_smartbutton1() -> None:

    source = """
SmartButton (b: Button) {
 initial final on -> on {
  b.pressed; b.released; 
 }
}"""

    expected = AutomataDevice(
        start_events=["on"],
        final_events=["on"],
        events=["on"],
        behavior=[("on", "on")],
        components={"b": "Button"},
        triggers={"on": Concat(Char("b.pressed"), Char("b.released"))},
    )
    assert expected == shelley2automata(
        ShelleyLanguage().transform(lark_parser.parse(source))
    )


def test_desklamp() -> None:

    source = """
DeskLamp (ledA: Led, ledB: Led, b: Button, t: Timer) {
 initial final level1 -> standby1, level2 {
  b.pressed; b.released; ledA.on; t.started; 
 }
 final level2 -> standby2 {
  b.pressed; b.released; {t.canceled; ledB.on;} + {ledB.on; t.canceled;} t.started; 
 }
 final standby1 -> level1 {
  t.timeout; ledA.off; 
 }
 final standby2 -> level1 {
  {b.pressed; b.released; t.canceled; } + {t.timeout; }{ledB.off; ledA.off; } + {ledA.off; ledB.off; }
 }
}
"""

    expected = AutomataDevice(
        start_events=["level1"],
        final_events=["level1", "level2", "standby1", "standby2"],
        events=["level1", "level2", "standby1", "standby2"],
        behavior=[
            ("level1", "standby1"),
            ("level1", "level2"),
            ("level2", "standby2"),
            ("standby1", "level1"),
            ("standby2", "level1"),
        ],
        components={"ledA": "Led", "ledB": "Led", "b": "Button", "t": "Timer"},
        triggers={
            "level1": Concat(
                left=Concat(
                    left=Concat(
                        left=Char(char="b.pressed"), right=Char(char="b.released")
                    ),
                    right=Char(char="ledA.on"),
                ),
                right=Char(char="t.started"),
            ),
            "level2": Concat(
                left=Concat(
                    left=Concat(
                        left=Char(char="b.pressed"), right=Char(char="b.released")
                    ),
                    right=Union(
                        left=Concat(
                            left=Char(char="t.canceled"), right=Char(char="ledB.on")
                        ),
                        right=Concat(
                            left=Char(char="ledB.on"), right=Char(char="t.canceled")
                        ),
                    ),
                ),
                right=Char(char="t.started"),
            ),
            "standby1": Concat(
                left=Char(char="t.timeout"), right=Char(char="ledA.off")
            ),
            "standby2": Concat(
                left=Union(
                    left=Concat(
                        left=Concat(
                            left=Char(char="b.pressed"), right=Char(char="b.released")
                        ),
                        right=Char(char="t.canceled"),
                    ),
                    right=Char(char="t.timeout"),
                ),
                right=Union(
                    left=Concat(
                        left=Char(char="ledB.off"), right=Char(char="ledA.off")
                    ),
                    right=Concat(
                        left=Char(char="ledA.off"), right=Char(char="ledB.off")
                    ),
                ),
            ),
        },
    )

    given = shelley2automata(ShelleyLanguage().transform(lark_parser.parse(source)))

    assert expected == given


def test_clickbutton():
    expected = AutomataDevice(
        start_events=["single", "double"],
        final_events=["single", "double"],
        events=["single", "double"],
        behavior=[
            ("single", "single"),
            ("single", "double"),
            ("double", "single"),
            ("double", "double"),
        ],
        components={"B": "Button", "T": "Timer"},
        triggers={
            "single": Concat(
                left=Concat(left=Char(char="B.press"), right=Char(char="T.begin")),
                right=Union(
                    left=Concat(
                        left=Char(char="T.timeout"), right=Char(char="B.release")
                    ),
                    right=Concat(
                        left=Char(char="B.release"), right=Char(char="T.timeout")
                    ),
                ),
            ),
            "double": Concat(
                left=Concat(
                    left=Concat(
                        left=Concat(
                            left=Char(char="B.press"), right=Char(char="T.begin")
                        ),
                        right=Char(char="B.release"),
                    ),
                    right=Union(
                        left=Concat(
                            left=Concat(
                                left=Char(char="B.press"), right=Char(char="T.timeout")
                            ),
                            right=Char(char="B.release"),
                        ),
                        right=Union(
                            left=Concat(
                                left=Concat(
                                    left=Char(char="B.press"),
                                    right=Char(char="B.release"),
                                ),
                                right=Char(char="T.end"),
                            ),
                            right=Char(char="T.end"),
                        ),
                    ),
                ),
                right=Char(char="B.press"),
            ),
        },
    )

    source = """
ClickButtonVariation (B: Button, T: Timer) {
 initial final single -> single, double {
  B.press; T.begin; {T.timeout; B.release; } + {B.release; T.timeout; }
 }
 initial final double -> single, double {
  B.press; 
  T.begin; 
  B.release; 
  {B.press; T.timeout; B.release; } + {B.press; B.release; T.end; } + {T.end; } # xor with 3 branches
  {B.press;} # xor with 1 branch Note: this becomes a Char when converted to Regex
 }
}"""
    given = shelley2automata(ShelleyLanguage().transform(lark_parser.parse(source)))

    assert expected == given
