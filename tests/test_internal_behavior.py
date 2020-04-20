from typing import Any, List
import yaml
from pathlib import Path
from karakuri.regular import Concat, Char, Union, NIL, concat, NFA, DFA, nfa_to_dfa
from .context import shelley
from shelley.automata import MicroBehavior, AssembledDevice, Device, build_external_behavior, build_components, \
    merge_components, MicroState

COMPILED_PATH = Path.cwd() / "tests" / "output"

B_P = "b.pressed"

LA_ON = "ledA.on"
LA_OFF = "ledA.off"

LB_ON = "ledB.on"
LB_OFF = "ledB.off"

LEVEL1 = "level1"
LEVEL2 = "level2"
OFF = "off"


def _remove_compiled_files(outdir: Path = None):
    for file in outdir.glob("*.sc[y,b]"):
        file.unlink()


def _remove_compiled_dir():
    _remove_compiled_files(COMPILED_PATH)
    try:
        COMPILED_PATH.rmdir()
    except FileNotFoundError:
        pass


def get_basic_devices():
    return dict(
        Led=Device(
            start_events=['on'],
            events=['on', 'off'],
            behavior=[
                ('on', 'off'),
                ('off', 'on'),
            ],
            components={},
            triggers={
                'on': NIL,
                'off': NIL,
            },
        ),
        Button=Device(
            start_events=['pressed'],
            events=['pressed'],
            behavior=[
                ('pressed', 'pressed')
            ],
            components={},
            triggers={
                'pressed': NIL
            },
        )
    )


def get_basic_known_devices():
    return dict((k, AssembledDevice.make(d, {}).external) for (k, d) in get_basic_devices().items())


def _serialize(name: str, data: Any) -> Path:
    path = COMPILED_PATH / "{0}.scy".format(name)
    with path.open(mode='w') as f:
        yaml.dump(data, f)
    return path


dev = Device(
    start_events=['level1'],
    events=['level1', 'level2', 'off'],
    behavior=[
        ('level1', 'level2'),
        ('level2', 'off'),
        ('off', 'level1')
    ],
    components={
        "b": "Button",
        "ledA": "Led",
        "ledB": "Led",
    },
    triggers={
        LEVEL1:
            Concat.from_list(map(Char, [
                B_P,
                LA_ON
            ])),
        LEVEL2:
            Concat.from_list(map(Char, [
                B_P,
                LB_ON
            ])),
        OFF:
            concat(
                Concat.from_list(map(Char, [B_P])),
                Union(
                    Concat.from_list(map(Char, [LB_OFF, LA_OFF])),
                    Concat.from_list(map(Char, [LA_OFF, LB_OFF])))
            )
    },
)

dev2 = Device(
    start_events=['level1'],
    events=['level1', 'off'],
    behavior=[
        ('level1', 'off'),
        ('off', 'level1')
    ],
    components={
        "b": "Button",
        "ledA": "Led",
    },
    triggers={
        LEVEL1:
            Concat.from_list(map(Char, [
                B_P,
                LA_ON
            ])),
        OFF:
            Concat.from_list(map(Char, [
                B_P,
                LA_OFF
            ]))
    },
)


def _encode(example_name: str):
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)

    external_behavior: NFA = build_external_behavior(dev2.behavior, dev2.start_events, dev2.events)
    print(external_behavior.as_dict(flatten=False))

    components_behaviors: dict[str, NFA] = dict(build_components(dev2.components, get_basic_known_devices()))
    for key, value in components_behaviors.items():
        print(value.as_dict(flatten=False))

    all_possible: DFA = merge_components(list(dict(components_behaviors).values()))
    print('all_possible alphabet: {alphabet}'.format(alphabet=all_possible.alphabet))  # frozenset of str
    path: Path = _serialize("{0}-all_possible_dfa".format(example_name), all_possible.minimize().as_dict())

    micro_behavior: MicroBehavior = MicroBehavior.make(external_behavior, dev2.triggers, all_possible.alphabet)
    micro_nfa_flatten = micro_behavior.nfa.flatten().as_dict()
    micro_dfa_flatten = micro_behavior.dfa.flatten().as_dict()
    micro_dfa_minimized_flatten = micro_behavior.dfa.minimize().as_dict()

    print("micro nfa flatten: ", micro_nfa_flatten)
    print("micro dfa flatten: ", micro_dfa_flatten)
    print("micro dfa flatten minimized: ", micro_dfa_minimized_flatten)
    path: Path = _serialize("{0}-micro_nfa".format(example_name), micro_nfa_flatten)
    path: Path = _serialize("{0}-micro_dfa_flatten".format(example_name), micro_nfa_flatten)
    path: Path = _serialize("{0}-micro_dfa_minimized_flatten".format(example_name), micro_dfa_minimized_flatten)
    print("micro nfa states: ", [state for state in micro_behavior.nfa.flatten().states])
    print("micro nfa state len: ", len([state for state in micro_behavior.nfa.flatten().states]))

    edges = [e for e in micro_behavior.nfa.edges]
    for src, char, dsts in edges:
        if isinstance(src, MicroState):
            # print(src)
            try:
                macro = set(src.macro).pop()
            except KeyError:
                macro = None

            try:
                micro = set(src.micro).pop()
            except KeyError:
                micro = None

            print("Micro: {macro}, {event}, {micro}".format(macro=macro, event=src.event, micro=micro))

        else:
            try:
                state = set(src.state).pop()
            except KeyError:
                state = None
            print("Macro: {state}".format(state=state))


def test_encode_behavior_dev():
    _encode("dev")


def test_encode_behavior_dev2():
    _encode("dev2")
