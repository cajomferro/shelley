from typing import List, Dict, Iterable, Tuple
from shelley.dfaapp.automaton import NFA
from shelley.dfaapp.regex import nfa_to_regex, regex_to_nfa, Union, Char, Empty, Nil, Concat, Star, Regex
from dataclasses import dataclass

def replace(r: Regex, rules: Dict[str, Regex]) -> Regex:
    if r is Nil:
        return r
    elif r is Empty:
        return r
    elif isinstance(r, Char):
        return rules.get(r.char, r)

    to_proc = [r]

    def do_subst(r, attr):
        child = getattr(r, attr)
        if isinstance(child, Char):
            new_child = rules.get(child.char, None)
            if new_child is not None and isinstance(new_child, str):
                raise ValueError(child.char)
            if new_child is not None:
                setattr(r, attr, new_child)
            return
        elif isinstance(child, Concat) or isinstance(
                child, Union) or isinstance(child, Star):
            to_proc.append(child)

    while len(to_proc) > 0:
        elem = to_proc.pop()
        if isinstance(elem, Star):
            do_subst(elem, "child")
        else:
            do_subst(elem, "left")
            do_subst(elem, "right")
    return r


def decode_triggers(behavior: NFA, triggers: Dict[str, Regex]) -> Regex:
    """
    Given an NFA and a map of decoders, returns a REGEX with all the
    substitutions performed.
    """
    # Convert the given triggers into a regex
    behavior_regex = nfa_to_regex(behavior)
    # Replace tokens by REGEX in decoder
    return replace(behavior_regex, triggers)

def build_behavior(behavior: Iterable[Tuple[str, str]], events:List[str]) -> NFA:
    states = ["begin_post"]
    for evt in events:
        states.append(evt + "_pre")
        states.append(evt + "_post")
    edges = []
    for (src, dst) in behavior:
        edges.add[(src + "_post", None, dst + "_pre")]
    for evt in events:
        edges.add[(evt + "_pre", evt, evt + "_post")]
    tsx = {}
    for (src, char, dst) in edges:
        out = tsx.get((src, char), None)
        if out is None:
            out = set()
            tsx[(src, char)] = out
        out.add(dst)

    return NFA(alphabet=frozenset(events),
        transition_func=lambda x,y: tsx[(x,y)],
        start_state="begin_post",
        accepted_states = list(evt + "_post" for evt in events))

def prefix_nfa(nfa:NFA, prefix:str) -> NFA:
    return NFA(alphabet=set(prefix + x for x in nfa.alphabet),
        transition_func=lambda src, char: nfa.transition_func(src, prefix + char),
        start_state=nfa.start_state, accepted_states=nfa.accepted_states)

def build_components(components:Dict[str, str], known_devices:Dict[str, NFA]) -> List[NFA]:
    result = []
    for (name, ty) in components.items():
        result.append(prefix_nfa(known_devices[ty], name + "."))
    return result

@dataclass
class Device:
    events:List[str]
    behavior:List[Tuple[str,str]]
    components:Dict[str, str]
    triggers:Dict[str,Regex]
    known_devices:Dict[str,NFA]

def check_valid_device(dev:Device):
    components = build_components(dev.components, dev.known_devices)
    behavior = build_behavior(dev.behavior, dev.events)
    check_valid(components, behavior, dev.triggers)

def check_valid(components: List[NFA], behavior: NFA, triggers: Dict[str, Regex], minimize=False,
                flatten=False) -> bool:
    # Get all tokens:
    alphabet = set()
    for c in components:
        alphabet.update(c.alphabet)
    # Shuffle all devices:
    dev = components.pop()
    for d in components:
        dev = dev.shuffle(d)
    # Convert the given NFA into a minimized DFA
    dev = dev.convert_to_dfa()
    if flatten:
        dev = dev.flatten(minimize=minimize)

    # Decode the triggers according to the decoder-map
    decoded_behavior = decode_triggers(behavior, triggers)
    decoded_behavior = regex_to_nfa(decoded_behavior, alphabet)
    # Convert into a minimized DFA
    decoded_behavior = decoded_behavior.convert_to_dfa()
    if flatten:
        decoded_behavior = decoded_behavior.flatten(minimize=minimize)
    # Ensure that the all possible behaviors in dev contain the decoded behavior
    return dev.contains(decoded_behavior)
