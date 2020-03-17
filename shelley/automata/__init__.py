from typing import List, Dict, Iterable, Tuple, Any, Optional, Collection
from karakuri.regular import NFA, nfa_to_regex, regex_to_nfa, Union, Char, Void, Nil, Concat, Star, Regex, nfa_to_dfa, DFA
from dataclasses import dataclass

def replace(r: Regex, rules: Dict[str, Regex]) -> Regex:
    if r is Void or r is Nil:
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


def build_behavior(behavior: Iterable[Tuple[str, str]], events:List[str]) -> NFA:
    states = ["begin_post"]
    for evt in events:
        states.append(evt + "_pre")
        states.append(evt + "_post")
    edges = []
    for (src, dst) in behavior:
        edges.append((src + "_post", None, dst + "_pre"))
    for evt in events:
        edges.append((evt + "_pre", evt, evt + "_post"))
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

def merge_components(components:Iterable[NFA[Any,str]], flatten:bool=False, minimize:bool=False) -> DFA[Any,str]:
    # Get the first component
    dev, *rst = components
    # Shuffle all devices:
    for d in rst:
        dev = dev.shuffle(d)
    # Convert the given NFA into a minimized DFA
    dev_dfa = nfa_to_dfa(dev)
    if flatten:
        dev_dfa = dev_dfa.flatten(minimize=minimize)
    return dev_dfa

def decode_behavior(behavior: Regex[str], triggers: Dict[str, Regex],
                alphabet:Optional[Collection[str]]=None,
                minimize:bool=False, flatten:bool=False) -> DFA[Any,str]:
    # Replace tokens by REGEX in decoder
    decoded_regex = replace(behavior, triggers)
    decoded_behavior = regex_to_nfa(decoded_regex, alphabet)
    # Convert into a minimized DFA
    decoded_behavior = nfa_to_dfa(decoded_behavior)
    if flatten:
        decoded_behavior = decoded_behavior.flatten(minimize=minimize)
    return decoded_behavior


def check_valid(components: List[NFA[Any,str]], behavior: Regex[str], triggers: Dict[str, Regex[str]], minimize=False,
                flatten=False) -> bool:
    all_possible = merge_components(components, flatten, minimize)
    decoded_behavior = decode_behavior(behavior, triggers, all_possible.alphabet, minimize, flatten)
    # Ensure that the all possible behaviors in dev contain the decoded behavior
    return all_possible.contains(decoded_behavior)
