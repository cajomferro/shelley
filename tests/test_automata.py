# from .context import shelley

from karakuri.regular import NFA, DFA, Nil, nfa_to_regex, regex_to_nfa, Union, Char, Concat, concat, shuffle as And, \
    nfa_to_dfa, Star, dfa_to_nfa, Void, NIL, VOID
from shelley.automata import get_invalid_behavior, decode_behavior, \
        build_components, CheckedDevice, prefix_nfa, build_behavior, \
        InvalidBehavior, mut_remove_star, flatten, eager_flatten

B_P = "b.pressed"
B_R = "b.released"


def create_button():
    return NFA(
        # states=[0, 1],
        alphabet=[B_P, B_R],
        transition_func=NFA.transition_edges([
            (0, [B_P], 1),
            (1, [B_R], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


LA_ON = "ledA.on"
LA_OFF = "ledA.off"


def create_led_a():
    return NFA(
        # states=[0, 1],
        alphabet=[LA_ON, LA_OFF],
        transition_func=NFA.transition_edges([
            (0, [LA_ON], 1),
            (1, [LA_OFF], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


LB_ON = "ledB.on"
LB_OFF = "ledB.off"


def create_led_b():
    return NFA(
        # states=[0, 1],
        alphabet=[LB_ON, LB_OFF],
        transition_func=NFA.transition_edges([
            (0, [LB_ON], 1),
            (1, [LB_OFF], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


T_T = "t.timeout"
T_C = "t.canceled"
T_S = "t.started"


def create_timer():
    return NFA(
        # states=[0, 1],
        alphabet=[T_T, T_C, T_S],
        transition_func=NFA.transition_edges([
            (0, [T_S], 1),
            (1, [T_C, T_T], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )


LEVEL1 = "level1"
LEVEL2 = "level2"
STANDBY1 = "standby1"
STANDBY2 = "standby2"


def create_hello_world():
    return NFA(
        alphabet=[LEVEL1, LEVEL2, STANDBY1, STANDBY2],
        transition_func=NFA.transition_edges([
            (0, [LEVEL1], 1),
            (1, [LEVEL2], 2),
            (1, [STANDBY1], 0),
            (2, [STANDBY2], 0),
        ]),
        start_state=0,
        accepted_states=lambda x: 0 <= x <= 2,
    )


def create_led_and_button():
    """
    This example should be a sub-behavior of shuffling button with led-a.
    
    (0) LEDA.ON --->  (1)  BTN.PRS ----> (2)
        <--- LEDA.OFF      <--- BTN.REL
    """
    return NFA(
        # states=[0, 1, 2],
        alphabet=[LA_ON, LA_OFF],
        transition_func=NFA.transition_edges([
            (0, [LA_ON], 1),
            (1, [LA_OFF], 0),
            (1, [B_P], 2),
            (2, [B_R], 1),
        ]),
        start_state=0,
        accepted_states=[0, 1, 2],
    )


def test_button():
    button = create_button()
    assert button.accepts([])
    assert button.accepts([B_P, B_R])
    assert button.accepts([B_P])
    assert not button.accepts([B_R])


def test_shuffle():
    button = create_button()
    led_a = create_led_a()
    both = button.shuffle(led_a)
    # Both should accept all behaviors of the button
    assert both.accepts([])
    assert both.accepts([B_P, B_R])
    assert both.accepts([B_P])
    assert not both.accepts([B_R])
    # It should also accept all behaviors of led
    assert both.accepts([LA_ON, LA_OFF])
    assert both.accepts([LA_ON])
    assert not both.accepts([LA_OFF])
    # Finally, it should accept interleaving of LED and Button:
    assert both.accepts([LA_ON, B_P, B_R, LA_OFF, B_P])
    # Here we fail because we have B_P followed by B_P
    assert not both.accepts([LA_ON, B_P, LA_OFF, B_P])


def test_led_and_button():
    both = create_led_and_button()
    # Both should accept all behaviors of the button
    assert both.accepts([])
    assert both.accepts([LA_ON])
    assert both.accepts([LA_ON, LA_OFF])
    # It should also accept all behaviors of led
    assert both.accepts([LA_ON, B_P])
    assert both.accepts([LA_ON, B_P, B_R, LA_OFF])
    assert both.accepts([LA_ON, B_P, B_R, LA_OFF, LA_ON])
    # Here we fail because we have B_P followed by B_P
    assert not both.accepts([B_R])
    assert not both.accepts([B_P])
    assert not both.accepts([LA_ON, B_R])
    assert not both.accepts([LA_ON, B_P, LA_OFF])


def test_contains():
    button = create_button()
    led_a = create_led_a()
    both = button.shuffle(led_a)
    behavior = create_led_and_button()
    assert nfa_to_dfa(both).contains(nfa_to_dfa(behavior))


def test_hello_world():
    HELLO_WORLD_TRIGGERS = {
        LEVEL1:
            Concat.from_list(map(Char, [B_P, B_R, LA_ON, T_S])),
        LEVEL2:
            Concat.from_list([
                Char(B_P),
                Char(B_R),
                And(Char(T_C), Char(LB_ON)),
                Char(T_S),
            ]),
        STANDBY1:
            concat(Char(T_T), Char(LA_OFF)),
        STANDBY2:
            concat(
                Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                And(Char(LB_OFF), Char(LA_OFF)),
            ),
    }
    components = [
        create_button(),
        create_led_a(),
        create_led_b(),
        create_timer()
    ]
    behavior = create_hello_world()
    assert get_invalid_behavior(components, nfa_to_regex(behavior), HELLO_WORLD_TRIGGERS) is None


def test_decode_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    be = decode_behavior(behavior, triggers, flatten=True, minimize=True)
    expected = nfa_to_dfa(regex_to_nfa(Star(Char(B_P)))).flatten(minimize=True)
    assert expected.contains(be)


def test_decode2():
    behavior = Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    triggers = {
        LEVEL1: Concat(Char(B_P), Char(B_P)),
        LEVEL2: NIL,
    }
    be = decode_behavior(behavior, triggers, flatten=True, minimize=True)
    expected = nfa_to_dfa(regex_to_nfa(Star(Concat(Char(B_P), Char(B_P))))).flatten(minimize=True)
    assert expected.contains(be)
    assert be.contains(expected)


def test_fail_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_P),
    }
    assert get_invalid_behavior([create_button()], behavior, triggers) is not None


def test_ok_1():
    behavior = Union(
        Char(LEVEL1),
        Star(Concat(Char(LEVEL1), Char(LEVEL2)))
    )
    triggers = {
        LEVEL1: Char(B_P),
        LEVEL2: Char(B_R),
    }
    assert get_invalid_behavior([create_button()], behavior, triggers) is None


def test_fail_hello_world():
    hello = create_hello_world()
    assert hello.accepts([])
    behavior = nfa_to_regex(hello)
    triggers = {
        LEVEL1:
            Concat.from_list(map(Char, [B_P, B_R, LA_ON, T_S])),
        LEVEL2:
            Concat.from_list([
                Char(B_R),
                Char(B_P),
                And(Char(T_C), Char(LB_ON)),
                Char(T_S),
            ]),
        STANDBY1:
            concat(Char(T_T), Char(LA_OFF)),
        STANDBY2:
            concat(
                Union(Concat.from_list(map(Char, [B_P, B_R, T_C])), Char(T_T)),
                And(Char(LB_OFF), Char(LA_OFF)),
            ),
    }
    components = [
        create_button(),
        create_led_a(),
        create_led_b(),
        create_timer()
    ]
    be = decode_behavior(behavior, triggers, flatten=True, minimize=True)
    assert be.accepts([])
    res = get_invalid_behavior(components, behavior, triggers)
    res = res.minimize()
    assert not res.accepts([])
    assert res is not None
    elems = list(list(w) for idx, w in zip(range(10), InvalidBehavior(res).sample(unique=True)))
    elems = list(map(list, elems))
    for seq in elems:
        assert res.accepts(seq)
    assert False

def test_flatten_regex():
    assert eager_flatten(Char('a')) == [['a']]
    assert eager_flatten(Concat(Char('a'), Char('b'))) == [ ['a', 'b'] ]
    assert eager_flatten(Union(Char('a'), Char('b'))) == [ ['a'], ['b'] ]
    assert eager_flatten(Concat(Char('a'), Union(Char('b'), Char('c')))) == [ ['a', 'b'], ['a', 'c'] ]
    assert eager_flatten(Union(Char('a'), Concat(Char('b'), Char('c')))) == [ ['a'], ['b', 'c'] ]
    assert eager_flatten(Concat(Char('a'), NIL)) == [['a']]
    assert eager_flatten(Concat(NIL, Char('a'))) == [['a']]
    assert eager_flatten(Union(VOID, Char('a'))) == [['a']]
    assert eager_flatten(Union(Char('a'), VOID)) == [['a']]

def test_mut_remove_star():
    assert mut_remove_star(NIL) is NIL
    assert mut_remove_star(VOID) is VOID
    assert mut_remove_star(Star(Char('a'))) is NIL
    assert mut_remove_star(Concat(Char('a'), Char('b'))) == Concat(Char('a'), Char('b'))
    #
    r = Concat(Char('a'), Star(Char('b')))
    assert r is mut_remove_star(r)
    assert r == Concat(Char('a'), NIL)
    #
    r = Union(Char('a'), Star(Char('b')))
    assert r is mut_remove_star(r)
    assert r == Union(Char('a'), NIL)

def test_prefix_nfa():
    led = NFA(
        alphabet=["on", "off"],
        transition_func=NFA.transition_edges([
            (0, ["on"], 1),
            (1, ["off"], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )
    assert prefix_nfa(led, "ledA.") == create_led_a()

def test_build_components():
    led = NFA(
        alphabet=["on", "off"],
        transition_func=NFA.transition_edges([
            (0, ["on"], 1),
            (1, ["off"], 0),
        ]),
        start_state=0,
        accepted_states=[0, 1],
    )
    comps = {
        "ledA": "LED",
        "ledB": "LED",
    }
    known_devs = {
        "LED": CheckedDevice(led),
    }
    given = dict(build_components(comps, known_devs))
    expected = {
        "ledA": create_led_a(),
        "ledB": create_led_b(),
    }
    assert expected == given
    assert len(expected) == len(given)
    for (ex, giv) in zip(expected, given):
        assert ex == giv

def test_build_behavior():
    start_events = ['level1']
    events = ['level1', 'standby1', 'level2', 'standby2']
    behavior = [
        ('level1', 'standby1'),
        ('level1', 'level2'),
        ('level2', 'standby2'),
        ('standby1', 'level1'),
        ('standby2', 'level1')
    ]
    tsx = [
        # Start events:
        ('start', 'level1', 'level1_post'),
        # (level1, standby1)
        ('level1_post', 'standby1', 'standby1_post'),
        ('level1_post', 'level2', 'level2_post'),
        ('level2_post', 'standby2', 'standby2_post'),
        ('standby1_post', 'level1', 'level1_post'),
        ('standby2_post', 'level1', 'level1_post'),
    ]
    accepted = set(x + "_post" for x in events)
    accepted.add("start")
    expected = NFA(alphabet=set(events),
        transition_func=NFA.transition_edges_split(tsx),
        start_state="start",
        accepted_states=accepted,
    )
    assert build_behavior(behavior, start_events, events) == expected
    # Make sure this is equivalent to HELLO WORLD
    assert nfa_to_dfa(build_behavior(behavior, start_events, events)).is_equivalent_to(nfa_to_dfa(create_hello_world()))
