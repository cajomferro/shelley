from typing import Any, List, Dict, Mapping, Optional
import yaml
from pathlib import Path
from karakuri.regular import (
    Concat,
    Char,
    Union,
    NIL,
    concat,
    NFA,
    DFA,
    nfa_to_dfa,
    dfa_to_nfa,
)
import shelley
from shelley.automata import (
    AssembledMicroBehavior,
    AssembledDevice,
    CheckedDevice,
    Device,
    DecodedState,
    build_external_behavior,
    build_components,
    MacroState,
    MicroState,
)

COMPILED_PATH = Path.cwd() / "_output" / "test-micro"

B_P = "b.pressed"

LA_ON = "l.on"
LA_OFF = "l.off"

LB_ON = "ledB.on"
LB_OFF = "ledB.off"

LEVEL1 = "level1"
LEVEL2 = "level2"
OFF = "off"


def _remove_compiled_files(outdir: Path):
    for file in outdir.glob("*.sc[y,b]"):
        file.unlink()


def _remove_compiled_dir():
    _remove_compiled_files(COMPILED_PATH)
    try:
        COMPILED_PATH.rmdir()
    except FileNotFoundError:
        pass


def get_basic_devices() -> Mapping[str, Device]:
    return dict(
        Led=Device(
            start_events=["on"],
            final_events=["on", "off"],
            events=["on", "off"],
            behavior=[("on", "off"), ("off", "on"),],
            components={},
            triggers={"on": NIL, "off": NIL,},
        ),
        Button=Device(
            start_events=["pressed"],
            final_events=["pressed"],
            events=["pressed"],
            behavior=[("pressed", "pressed")],
            components={},
            triggers={"pressed": NIL},
        ),
    )


def get_basic_known_devices() -> Mapping[str, CheckedDevice]:
    return dict(
        (k, AssembledDevice.make(d, {}).external)
        for (k, d) in get_basic_devices().items()
    )


def _serialize(name: str, data: Any) -> Path:
    path = COMPILED_PATH / "{0}.scy".format(name)
    with path.open(mode="w") as f:
        yaml.dump(data, f)
    return path


# dev = Device(
#     start_events=['level1'],
#     events=['level1', 'level2', 'off'],
#     behavior=[
#         ('level1', 'level2'),
#         ('level2', 'off'),
#         ('off', 'level1')
#     ],
#     components={
#         "b": "Button",
#         "l": "Led",
#         "ledB": "Led",
#     },
#     triggers={
#         LEVEL1:
#             Concat.from_list(map(Char, [
#                 B_P,
#                 LA_ON
#             ])),
#         LEVEL2:
#             Concat.from_list(map(Char, [
#                 B_P,
#                 LB_ON
#             ])),
#         OFF:
#             concat(
#                 Concat.from_list(map(Char, [B_P])),
#                 Union(
#                     Concat.from_list(map(Char, [LB_OFF, LA_OFF])),
#                     Concat.from_list(map(Char, [LA_OFF, LB_OFF])))
#             )
#     },
# )

# this device is equivalent to example desklamp/good_simple_desklamp2
dev = Device(
    start_events=["level1"],
    final_events=["level1", "off"],
    events=["level1", "off"],
    behavior=[("level1", "off"), ("off", "level1")],
    components={"b": "Button", "l": "Led",},
    triggers={
        LEVEL1: Concat.from_list([Char(B_P), Char(LA_ON)]),
        OFF: Concat.from_list([Char(B_P), Char(LA_OFF)]),
    },
)


def _encode(example_name: str):
    COMPILED_PATH.mkdir(parents=True, exist_ok=True)

    external_behavior: NFA = build_external_behavior(
        dev.behavior, dev.start_events, dev.events, dev.events
    )
    print("\nmacro nfa flatten=False", external_behavior.as_dict(flatten=False))
    print("macro nfa flatten=True", external_behavior.as_dict(flatten=True))

    components_behaviors: Dict[str, NFA] = dict(
        build_components(dev.components, get_basic_known_devices())
    )
    for key, value in components_behaviors.items():
        print(value.as_dict(flatten=False))

    micro_be: AssembledMicroBehavior = AssembledMicroBehavior.make(
        components=list(components_behaviors.values()),
        external_behavior=external_behavior,
        triggers=dev.triggers,
    )

    # shuffle = interleave = all possible
    # all_possible: DFA = merge_components(list(dict(components_behaviors).values()))
    all_possible: DFA = micro_be.possible
    _serialize("{0}-all-possible-dfa".format(example_name), all_possible.as_dict())
    _serialize(
        "{0}-all-possible-dfa-minimized-traps".format(example_name),
        all_possible.minimize().as_dict(),
    )
    _serialize(
        "{0}-all-possible-dfa-minimized-notraps".format(example_name),
        dfa_to_nfa(all_possible).remove_all_sink_states().as_dict(),
    )

    # micro NFA
    micro_nfa_no_epsilon_no_traps = (
        micro_be.nfa.remove_epsilon_transitions().remove_all_sink_states().as_dict()
    )
    _serialize(
        "{0}-micro-nfa-no-epsilon-no-traps".format(example_name),
        micro_nfa_no_epsilon_no_traps,
    )

    micro_nfa = micro_be.nfa.flatten().as_dict()
    _serialize("{0}-micro-nfa".format(example_name), micro_nfa)

    micro_nfa_no_epsilon = micro_be.nfa.remove_epsilon_transitions().as_dict()
    _serialize("{0}-micro-nfa-no-epsilon".format(example_name), micro_nfa_no_epsilon)

    micro_nfa_no_traps = micro_be.nfa.remove_all_sink_states().as_dict()
    _serialize("{0}-micro-nfa-no-traps".format(example_name), micro_nfa_no_traps)

    # micro DFA
    micro_dfa = micro_be.dfa.flatten()
    _serialize("{0}-micro-dfa".format(example_name), micro_dfa.as_dict())
    assert len([state for state in micro_dfa.states]) == 31

    micro_dfa_minimized = micro_be.dfa.minimize().flatten()
    _serialize(
        "{0}-micro-dfa-minimized".format(example_name), micro_dfa_minimized.as_dict()
    )
    assert len([state for state in micro_dfa_minimized.states]) == 5

    micro_dfa_minimized_no_traps = dfa_to_nfa(
        micro_be.dfa.minimize()
    ).remove_all_sink_states()
    _serialize(
        "{0}-micro-dfa-minimized-no-traps".format(example_name),
        micro_dfa_minimized_no_traps.as_dict(),
    )
    assert len([state for state in micro_dfa_minimized_no_traps.states]) == 4

    print("micro nfa states: ", [state for state in micro_be.nfa.flatten().states])
    print(
        "micro nfa state len: ", len([state for state in micro_be.nfa.flatten().states])
    )

    edges = [e for e in micro_be.nfa.edges]
    for src, char, dsts in edges:
        if isinstance(src, MicroState):
            # print(src)
            try:
                macro: Optional[str] = set(src.macro).pop()
            except KeyError:
                macro = None

            try:
                micro: Optional[str] = set(src.micro).pop()
            except KeyError:
                micro = None

            print(
                "Micro: {macro}, {event}, {micro}".format(
                    macro=macro, event=src.event, micro=micro
                )
            )

        elif isinstance(src, MacroState):
            try:
                state: Optional[str] = set(src.state).pop()
            except KeyError:
                state = None
            print("Macro: {state}".format(state=state))
        else:
            assert False


def test_encode_behavior_dev():
    _encode(
        "dev"
    )  # this device is equivalent to example desklamp/good_simple_desklamp2
