from typing import Any, List
import yaml
from pathlib import Path
from karakuri.regular import Concat, Char, Union, NIL, concat, NFA, DFA, nfa_to_dfa
from .context import shelley
from shelley import automata

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
        Led=automata.Device(
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
        Button=automata.Device(
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
    return dict((k, automata.assemble_device(d, {}).external) for (k, d) in get_basic_devices().items())


def _serialize(name: str, data: Any) -> Path:
    path = COMPILED_PATH / "{0}.scy".format(name)
    with path.open(mode='w') as f:
        yaml.dump(data, f)
    return path


dev = automata.Device(
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

dev2 = automata.Device(
    start_events=['level1'],
    events=['level1', 'off'],
    behavior=[
        ('level1', 'level1'),
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


def test_merge_components():
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)

    external_behavior: NFA = automata.build_external_behavior(dev.behavior, dev.start_events, dev.events)
    print(external_behavior.as_dict(flatten=False))
    path: Path = _serialize("simple_desklamp_external", external_behavior.as_dict(flatten=False))

    components_behaviors: dict[str, NFA] = dict(automata.build_components(dev.components, get_basic_known_devices()))
    for key, value in components_behaviors.items():
        path: Path = _serialize("{0}_external".format(key), value.as_dict(flatten=False))
        print(value.as_dict(flatten=False))

    all_possible: NFA = _merge_components(list(dict(components_behaviors).values()))
    all_possible_as_dict = all_possible.as_dict(flatten=False)
    print(all_possible_as_dict)
    path: Path = _serialize("simple_desklamp_nfa", all_possible_as_dict)
    dfa_all_possible_as_dict = nfa_to_dfa(all_possible).as_dict(flatten=False)
    print(dfa_all_possible_as_dict)
    path: Path = _serialize("simple_desklamp_dfa", dfa_all_possible_as_dict)

    # _remove_compiled_dir()


def test_encode_behavior_external_dev():
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)

    external_behavior: NFA = automata.build_external_behavior(dev.behavior, dev.start_events, dev.events)
    print(external_behavior.as_dict(flatten=False))

    components_behaviors: dict[str, NFA] = dict(automata.build_components(dev.components, get_basic_known_devices()))
    for key, value in components_behaviors.items():
        print(value.as_dict(flatten=False))

    all_possible: DFA = automata.merge_components(list(dict(components_behaviors).values()))

    internal_behavior: NFA = automata.encode_behavior_ex(external_behavior, dev.triggers, all_possible.alphabet)
    print(internal_behavior.as_dict(flatten=False))
    path: Path = _serialize("encoded_nfa", internal_behavior.as_dict(flatten=False))
    print([state for state in internal_behavior.states])
    print(len([state for state in internal_behavior.states]))


def test_encode_behavior_external_dev2():
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)

    external_behavior: NFA = automata.build_external_behavior(dev2.behavior, dev2.start_events, dev2.events)
    print(external_behavior.as_dict(flatten=False))

    components_behaviors: dict[str, NFA] = dict(automata.build_components(dev2.components, get_basic_known_devices()))
    for key, value in components_behaviors.items():
        print(value.as_dict(flatten=False))

    all_possible: DFA = automata.merge_components(list(dict(components_behaviors).values()))
    print('all_possible alphabet: {alphabet}'.format(alphabet=all_possible.alphabet))  # frozenset of str

    internal_behavior: NFA = automata.encode_behavior_ex(external_behavior, dev2.triggers, all_possible.alphabet)
    print(internal_behavior.as_dict(flatten=False))
    path: Path = _serialize("encoded_nfa", internal_behavior.as_dict(flatten=False))
    print([state for state in internal_behavior.states])
    print(len([state for state in internal_behavior.states]))

    edges = [e for e in internal_behavior.edges]
    for src, char, dsts in edges:
        if isinstance(src, automata.MicroState):
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
