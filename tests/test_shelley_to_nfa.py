# Shelley to NFA[S,A] --> S: state type (str or int), A: alphabet type (str)

from karakuri.regular import Char, Concat, Union, NIL

from shelley.automata import Device as AutomataDevice
from shelley.shelley2automata import shelley2automata
from shelley import yaml2shelley


def test_button() -> None:

    yaml_src = """
  name: Button
  operations:
    pressed:
      start: true
      final: true
      next: [released]
    released:
      start: false
      final: true
      next: [pressed]
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
        yaml2shelley.get_shelley_from_yaml_str(yaml_src)
    )


def test_led() -> None:

    yaml_src = """
  name: Led
  operations:
    on:
      start: true
      final: true
      next: [off]
    off:
      start: false
      final: true
      next: [on]
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
        yaml2shelley.get_shelley_from_yaml_str(yaml_src)
    )


def test_timer() -> None:

    yaml_src = """
  name: Timer
  operations:
    started:
        start: True
        final: true
        next: [canceled, timeout]
    canceled:
        start: False
        final: True
        next: [started]
    timeout:
        start: False
        final: True
        next: [started]
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
        yaml2shelley.get_shelley_from_yaml_str(yaml_src)
    )


def test_smartbutton1() -> None:

    yaml_src = """
  name: SmartButton
  components:
    b: Button
  operations:
    on:
        start: True
        final: True
        micro: [ b.pressed, b.released]
        next: [on]
    """

    expected = AutomataDevice(
        start_events=["on"],
        final_events=["on"],
        events=["on"],
        behavior=[("on", "on")],
        components={"b": "Button"},
        triggers={"on": Concat(Char("b.pressed"), Char("b.released"))},
    )
    assert expected == shelley2automata(
        yaml2shelley.get_shelley_from_yaml_str(yaml_src)
    )


def test_desklamp() -> None:

    yaml_src = """
  name: DeskLamp
  components:
    ledA: Led
    ledB: Led
    b: Button
    t: Timer
  operations:
    level1:
        start: True
        micro: [b.pressed, b.released, ledA.on, t.started]
        next: [standby1, level2]
    level2:
        next: [standby2]
        micro:
          - b.pressed
          - b.released
          - xor:
              - [t.canceled, ledB.on]
              - [ledB.on, t.canceled]
          - t.started
    standby1:
        next: [level1]
        micro: [t.timeout, ledA.off]
    standby2:
        next: [level1]
        micro:
          - xor:
              - [b.pressed, b.released, t.canceled]
              -  t.timeout
          - xor:
                - [ledB.off, ledA.off]
                - [ledA.off, ledB.off]
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
        components={"b": "Button", "ledA": "Led", "ledB": "Led", "t": "Timer"},
        triggers={
            "level1": Concat(
                Char("b.pressed"),
                Concat(Char("b.released"), Concat(Char("ledA.on"), Char("t.started"))),
            ),
            "level2": Concat(
                Char("b.pressed"),
                Concat(
                    Char("b.released"),
                    Concat(
                        Union(
                            Concat(Char("t.canceled"), Char("ledB.on")),
                            Concat(Char("ledB.on"), Char("t.canceled")),
                        ),
                        Char("t.started"),
                    ),
                ),
            ),
            "standby1": Concat(Char("t.timeout"), Char("ledA.off")),
            "standby2": Concat(
                Union(
                    Concat(
                        Char("b.pressed"),
                        Concat(Char("b.released"), Char("t.canceled")),
                    ),
                    Char("t.timeout"),
                ),
                Union(
                    Concat(Char("ledB.off"), Char("ledA.off")),
                    Concat(Char("ledA.off"), Char("ledB.off")),
                ),
            ),
        },
    )
    given = shelley2automata(yaml2shelley.get_shelley_from_yaml_str(yaml_src))
    assert isinstance(given.triggers["level2"], Concat)
    x = given.triggers["level2"].right
    assert isinstance(expected.triggers["level2"], Concat)
    y = expected.triggers["level2"].right
    assert isinstance(x, Concat) and isinstance(y, Concat) and x.right == y.right
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
                    left=Char(char="B.press"),
                    right=Concat(
                        left=Char(char="T.begin"), right=Char(char="B.release")
                    ),
                ),
                right=Concat(
                    left=Union(
                        left=Union(
                            left=Concat(
                                left=Char(char="B.press"),
                                right=Concat(
                                    left=Char(char="T.timeout"),
                                    right=Char(char="B.release"),
                                ),
                            ),
                            right=Concat(
                                left=Char(char="B.press"),
                                right=Concat(
                                    left=Char(char="B.release"),
                                    right=Char(char="T.end"),
                                ),
                            ),
                        ),
                        right=Char(char="T.end"),
                    ),
                    right=Char(char="B.press"),
                ),
            ),
        },
    )

    yaml_code = """

 name: ClickButtonVariation
 components:
  B: Button
  T: Timer
 operations:
    single:
       next: $ANY
       start: True
       final: True
       micro:
         seq:
         - seq: [B.press, T.begin]
         - xor:
           - seq: [T.timeout, B.release] # user ir slow
           - seq: [B.release, T.timeout] # user is fast
    double:
       next: $ANY
       start: True
       final: True
       micro:
         seq:
         - seq: [B.press, T.begin, B.release]
         - xor:
           - seq: [B.press, T.timeout, B.release] # user is slow
           - seq: [B.press, B.release, T.end] # user is fast
           - T.end
         - xor: # Note: this becomes a Char when converted to Regex
            - B.press
    """
    given = shelley2automata(yaml2shelley.get_shelley_from_yaml_str(yaml_code))

    assert isinstance(given.triggers["double"], Concat)
    assert isinstance(expected.triggers["double"], Concat)

    # seq:
    # - seq: [B.press, T.begin, B.release] (LEFT)
    # ...
    seq_given = given.triggers["double"].left
    seq_expected = expected.triggers["double"].left
    assert (
        isinstance(seq_given, Concat)
        and isinstance(seq_expected, Concat)
        and seq_given.left == seq_expected.left
    )

    # seq:
    # ...
    # - xor: (RIGHT, LEFT)
    #   - seq: [B.press, T.timeout, B.release] # user is slow
    #   - seq: [B.press, B.release, T.end] # user is fast
    #   - T.end
    # ...
    xor_given = given.triggers["double"].right.left
    xor_expected = expected.triggers["double"].right.left
    assert (
        isinstance(xor_given, Union)
        and isinstance(xor_expected, Union)
        and xor_given.right == xor_expected.right
    )

    assert (
        isinstance(xor_given.left.left, Concat)
        and isinstance(xor_expected.left.left, Concat)
        and xor_given.left.left == xor_expected.left.left
    )

    # seq:
    # ...
    # - xor: # Note: this becomes a Char when converted to Regex (RIGHT, RIGHT)
    #    - B.press
    xor_given2 = given.triggers["double"].right.right
    xor_expected2 = expected.triggers["double"].right.right
    assert (
        isinstance(xor_given2, Char)
        and isinstance(xor_expected2, Char)
        and xor_given2.char == xor_expected2.char
    )

    assert expected == given
