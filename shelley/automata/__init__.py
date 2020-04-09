from typing import List, Dict, Iterable, Tuple, Any, Optional, Collection, Mapping, Set, Iterator
import typing
from karakuri.regular import NFA, nfa_to_regex, regex_to_nfa, Union, Char, NIL, Concat, Star, Regex, nfa_to_dfa, \
    DFA, dfa_to_nfa, Nil, Void, RegexHandler, SubstHandler, VOID
from dataclasses import dataclass
import copy
import itertools

@dataclass
class Device:
    start_events: List[str]
    events: List[str]
    behavior: List[Tuple[str, str]]
    components: Dict[str, str]
    triggers: Dict[str, Regex]

@dataclass
class CheckedDevice:
    nfa: NFA[Any, str]


@dataclass
class InvalidBehavior:
    error_trace: List[str]
    component_errors: Dict[str, Tuple[List[str], int]]


class ReplaceHandler(SubstHandler):
    def __init__(self, subst):
        self.subst = subst

    def on_char(self, char):
        result = self.subst.get(char.char, None)
        return char if result is None else result


def replace(r: Regex, rules: Dict[str, Regex]) -> Regex:
    return r.fold(ReplaceHandler(rules))

# XXX: make the start_state not be a string
def build_behavior(behavior: Iterable[Tuple[str, str]], start_events:List[str], events: List[str], start_state="$START") -> NFA[Any, str]:
    states = []
    for evt in events:
        states.append(evt)
    if start_state in events:
        raise ValueError(f"Start state '{start_state}' cannot have the same name as an event.")
    states.append(start_state)
    edges: List[Tuple[str, Optional[str], str]] = []
    for (src, dst) in behavior:
        edges.append((src, dst, dst))
    for evt in start_events:
        edges.append((start_state, evt, evt))
    tsx: Dict[Tuple[str, Optional[str]], Set[str]] = {}
    for (src, char, dst) in edges:
        out = tsx.get((src, char), None)
        if out is None:
            out = set()
            tsx[(src, char)] = out
        out.add(dst)
    accepted = list(evt for evt in events)
    accepted.append(start_state)

    return NFA(alphabet=frozenset(events),
               transition_func=NFA.transition_table(tsx),
               start_state=start_state,
               accepted_states=set(accepted))

def prefix_nfa(nfa: NFA, prefix: str) -> NFA:
    old_tsx_func = nfa.transition_func
    offset = len(prefix)
    def transition_func(src, char):
        new_char = None if char is None else char[offset:]
        return old_tsx_func(src, new_char)
    return NFA(
        alphabet=set(prefix + x for x in nfa.alphabet),
        transition_func=transition_func,
        start_state=nfa.start_state,
        accepted_states=nfa.accepted_states
    )


def build_components(components: Dict[str, str], known_devices: Mapping[str, CheckedDevice]) -> List[NFA]:
    result = []
    for (name, ty) in components.items():
        yield (name, prefix_nfa(known_devices[ty].nfa, name + "."))


def merge_components(components: Iterable[NFA[Any, str]], flatten: bool = False, minimize: bool = False) -> DFA[
    Any, str]:
    # Get the first component
    dev, *rst = components
    # Shuffle all devices:
    for d in rst:
        dev = dev.shuffle(d)
    # Convert the given NFA into a minimized DFA
    dev_dfa = nfa_to_dfa(dev)
    if flatten:
        return dev_dfa.flatten(minimize=minimize)
    return dev_dfa


def encode_behavior(behavior: Regex[str], triggers: Dict[str, Regex],
                    alphabet: Optional[Collection[str]] = None,
                    minimize: bool = False, flatten: bool = False) -> DFA[Any, str]:
    # Replace tokens by REGEX in encoder
    encoded_regex = replace(behavior, triggers)
    encoded_behavior = regex_to_nfa(encoded_regex, alphabet)
    # Convert into a minimized DFA
    encoded_behavior_dfa = nfa_to_dfa(encoded_behavior)
    if flatten:
        return encoded_behavior_dfa.flatten(minimize=minimize)
    return encoded_behavior_dfa

@dataclass(frozen=True)
class DecodedState:
    pass

@dataclass(frozen=True, order=True)
class MacroState(DecodedState):
    state: str

@dataclass(frozen=True, order=True)
class MicroState(DecodedState):
    # The next macro state
    macro: str
    # The event that we are processing
    event: str
    # The current micro state
    micro: str

    def advance_micro(self, micro:str):
        return MicroState(macro=self.macro, event=self.event, micro=micro)

    def advance_macro(self):
        return MacroState(self.macro)

@dataclass
class AmbiguousTriggers:
    nfa:NFA
    states:Any

def encode_behavior2(behavior: DFA[Any,str], triggers: Dict[str, DFA], alphabet:Optional[Collection[str]] = None):
    def tsx(src, char):
        if isinstance(src, MacroState):
            if char is not None:
                return frozenset()
            # Macro-state
            result = set()
            for evt in behavior.alphabet:
                result.add(MicroState(
                    macro=behavior.transition_func(src.state, evt),
                    event=evt,
                    micro=triggers[evt].start_state
                ))
            return frozenset(result)
        elif isinstance(src, MicroState):
            dfa = triggers[src.event]
            if dfa.accepted_states(src.micro) and char is None:
                return frozenset([src.advance_macro()])
            elif char in dfa.alphabet:
                dst = src.advance_micro(dfa.transition_func(src.micro, char))
                return frozenset([dst])
            return frozenset()
        else:
            raise ValueError("Unknown state", src, char)

    def is_final(st):
        return isinstance(st, MacroState) and behavior.accepted_states(st.state)

    if alphabet is None:
        # Infer the alphabet from each trigger
        alphabet = set()
        for dfa in triggers.values():
            alphabet.update(dfa.alphabet)

    nfa = NFA(
        alphabet=alphabet,
        transition_func=tsx,
        start_state=MacroState(behavior.start_state),
        accepted_states=is_final
    )
    dfa = nfa_to_dfa(nfa)
    # Check if there are concurrent macro-states
    ambiguous_states = []
    for st in dfa.states:
        row = list(filter(lambda x: isinstance(x, MacroState), st))
        if len(row) > 1:
            ambiguous_states.append(row)
    if len(ambiguous_states) > 0:
        return AmbiguousTriggers(nfa, ambiguous_states)
    return nfa


def get_invalid_behavior(components: List[NFA[Any, str]], behavior: Regex[str], triggers: Dict[str, Regex[str]],
                         minimize=False,
                         flatten=False) -> Optional[DFA[Any, str]]:
    if len(components) == 0:
        return None
    all_possible = merge_components(components, flatten, minimize)
    encoded_behavior = encode_behavior(behavior, triggers, all_possible.alphabet, minimize, flatten)
    # Ensure that the all possible behaviors in dev contain the encoded behavior
    invalid_behavior = encoded_behavior.subtract(all_possible)
    if invalid_behavior.is_empty():
        return None
    else:
        return invalid_behavior

def ensure_well_formed(dev: Device):
    evts = set(dev.events)
    start_evts = set(dev.start_events)
    if not (start_evts <= evts):
        return ValueError("start_events must be included in events, got these extra: ", start_evts - evts)
    # Get keys
    trigs = set(dev.triggers)
    if not (trigs <= evts):
        return ValueError("All events must be defined in triggers. These triggers are undefined events: ", trigs - evts)
    if trigs != evts:
        return ValueError("The following trigger rules were not defined: ", evts - trigs)

def demultiplex(seq:List[str]) -> Mapping[str,List[str]]:
    sequences = dict()
    for msg in seq:
        component, op = msg.split(".")
        component_seq = sequences.get(component, None)
        if component_seq is None:
            sequences[component] = component_seq = []
        component_seq.append(op)
    return sequences

def check_valid_device(dev: Device, known_devices: Mapping[str, CheckedDevice]) -> typing.Union[CheckedDevice, InvalidBehavior]:
    ensure_well_formed(dev)
    components = list(dict(build_components(dev.components, known_devices)).values())
    behavior = build_behavior(dev.behavior, dev.start_events, dev.events)
    inv_behavior = get_invalid_behavior(components, nfa_to_regex(behavior), dev.triggers)
    if inv_behavior is None:
        return CheckedDevice(behavior)
    else:
        # We compute the smallest error
        dec_seq = inv_behavior.get_shortest_string()
        # We demutex by device
        errs = dict()
        for component, seq in demultiplex(dec_seq).items():
            ch_dev = known_devices[dev.components[component]]
            if not ch_dev.nfa.accepts(seq):
                dfa = nfa_to_dfa(ch_dev.nfa).minimize()
                errs[component] = (seq, dfa.get_divergence_index(seq))


        return InvalidBehavior(dec_seq, errs)
