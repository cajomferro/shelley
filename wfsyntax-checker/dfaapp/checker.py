from typing import List, Dict
from dfaapp.automaton import NFA
from dfaapp.regex import nfa_to_regex, regex_to_nfa, Union, Char, Empty, Nil, Concat, Star, concat, op_and as And, Regex


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


def check_valid(components: List[NFA], behavior: NFA, triggers: Dict[str, Regex]) -> bool:
    # Get all tokens:
    alphabet = set()
    for c in components:
        alphabet.update(c.alphabet)
    # Shuffle all devices:
    dev = components.pop()
    for d in components:
        dev = dev.shuffle(d)
    # Convert the given NFA into a minimized DFA
    dev = dev.convert_to_dfa().flatten()

    # Decode the triggers according to the decoder-map
    decoded_behavior = decode_triggers(behavior, triggers)
    decoded_behavior = regex_to_nfa(decoded_behavior, alphabet)
    # Convert into a minimized DFA
    decoded_behavior = decoded_behavior.convert_to_dfa().flatten()
    # Ensure that the all possible behaviors in dev contain the decoded behavior
    return dev.contains(decoded_behavior)
