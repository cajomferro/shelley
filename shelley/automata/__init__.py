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
    dfa: DFA[Any, str]
    def sample(self, unique=False):
        """
        Sample invalid sequences.
        """
        r = nfa_to_regex(dfa_to_nfa(self.dfa))
        r = remove_star(r)
        result = flatten(r)
        if result is None:
            return
        else:
            if unique:
                known = set()
                for k in result:
                    k = tuple(k)
                    if k not in known:
                        yield k
                        known.add(k)
            else:
                yield from result
    def get_smallest_error(self):
        r = nfa_to_regex(dfa_to_nfa(self.dfa))
        return smallest_string(r)


class RemoveStarHandler(SubstHandler):
    """
    Same as subst-handler, but 
    """
    def on_star(self, reg, child):
        return NIL

REMOVE_STAR_HANDLER = RemoveStarHandler()

def remove_star(r: Regex) -> Regex:
    return r.fold(REMOVE_STAR_HANDLER)

def flatten_union(left, right):
    for l, r in itertools.product(left, right):
        yield itertools.chain(l, r)

def eager_flatten(r):
    """
    Generates iterator
    :param r:
    :return:
    """
    result = flatten(r)
    if result is None:
        return None
    else:
        return list(map(list, result))

class FlattenHandler(RegexHandler):
    on_nil = ( () ,)
    on_void = None
    def on_char(self, r):
        return ( (r.char ,)   ,)
    def on_star(self, r, child):
        raise ValueError("Does not support star: ", r)
    def on_union(self, r, left, right):
        if left is None:
            return right
        if right is None:
            return left
        return itertools.chain(left, right)
    def on_concat(self, r, left, right):
        if left is None or right is None:
            return None
        return flatten_union(left, right)
# We only need one instance
FLATTEN_HANDLER = FlattenHandler()

def flatten(r: Regex) -> Optional[Iterator[Tuple[str]]]:
    return r.fold(FLATTEN_HANDLER)

class SmallestHandler(RegexHandler):
    on_nil = tuple([])
    on_void = None
    def on_char(self, r):
        return tuple([r.char])
    def on_union(self, r, left, right):
        if left is None:
            return right
        if right is None:
            return left
        return left if len(left) < len(right) else right
    def on_concat(self, r, left, right):
        if left is None:
            return None
        if right is None:
            return None
        return left + right
    def on_star(self, r, child):
        return tuple([])

SMALLEST_HANDLER = SmallestHandler()
def smallest_string(r:Regex):
    return r.fold(SMALLEST_HANDLER)

class ReplaceHandler(SubstHandler):
    def __init__(self, subst):
        self.subst = subst

    def on_char(self, char):
        result = self.subst.get(char.char, None)
        return char if result is None else result


def replace(r: Regex, rules: Dict[str, Regex]) -> Regex:
    return r.fold(ReplaceHandler(rules))


def build_behavior(behavior: Iterable[Tuple[str, str]], start_events:List[str], events: List[str]) -> NFA[Any, str]:
    states = ["start"]
    for evt in events:
        states.append(evt + "_pre")
        states.append(evt + "_post")
    edges: List[Tuple[str, Optional[str], str]] = []
    for (src, dst) in behavior:
        edges.append((src + "_post", dst, dst + "_post"))
    for evt in start_events:
        edges.append(("start", evt, evt + "_post"))
    tsx: Dict[Tuple[str, Optional[str]], Set[str]] = {}
    for (src, char, dst) in edges:
        out = tsx.get((src, char), None)
        if out is None:
            out = set()
            tsx[(src, char)] = out
        out.add(dst)
    accepted = list(evt + "_post" for evt in events)
    accepted.append("start")

    return NFA(alphabet=frozenset(events),
               transition_func=NFA.transition_table(tsx),
               start_state="start",
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


def decode_behavior(behavior: Regex[str], triggers: Dict[str, Regex],
                    alphabet: Optional[Collection[str]] = None,
                    minimize: bool = False, flatten: bool = False) -> DFA[Any, str]:
    # Replace tokens by REGEX in decoder
    decoded_regex = replace(behavior, triggers)
    decoded_behavior = regex_to_nfa(decoded_regex, alphabet)
    # Convert into a minimized DFA
    decoded_behavior_dfa = nfa_to_dfa(decoded_behavior)
    if flatten:
        return decoded_behavior_dfa.flatten(minimize=minimize)
    return decoded_behavior_dfa


def get_invalid_behavior(components: List[NFA[Any, str]], behavior: Regex[str], triggers: Dict[str, Regex[str]],
                         minimize=False,
                         flatten=False) -> Optional[DFA[Any, str]]:
    if len(components) == 0:
        return None
    all_possible = merge_components(components, flatten, minimize)
    decoded_behavior = decode_behavior(behavior, triggers, all_possible.alphabet, minimize, flatten)
    # Ensure that the all possible behaviors in dev contain the decoded behavior
    invalid_behavior = decoded_behavior.subtract(all_possible)
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



def check_valid_device(dev: Device, known_devices: Mapping[str, CheckedDevice]) -> typing.Union[CheckedDevice, InvalidBehavior]:
    ensure_well_formed(dev)
    components = list(dict(build_components(dev.components, known_devices)).values())
    behavior = build_behavior(dev.behavior, dev.start_events, dev.events)
    inv_behavior = get_invalid_behavior(components, nfa_to_regex(behavior), dev.triggers)
    if inv_behavior is None:
        return CheckedDevice(behavior)
    else:
        return InvalidBehavior(inv_behavior)
