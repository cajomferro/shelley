from typing import List, Dict, Iterable, Tuple, Any, Optional, Collection, \
    Mapping, Set, Iterator, Callable, AbstractSet
import typing
from karakuri.regular import NFA, nfa_to_regex, regex_to_nfa, Union, Char, NIL, Concat, Star, Regex, nfa_to_dfa, \
    DFA, dfa_to_nfa, Nil, Void, RegexHandler, SubstHandler, VOID
from dataclasses import dataclass, field
import copy
import itertools
from karakuri import hml


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


KnownDevices = Mapping[str, CheckedDevice]


@dataclass(frozen=True)
class DecodedState:
    pass


class ReplaceHandler(SubstHandler[str]):
    def __init__(self, subst: Dict[str, Regex[str]]):
        self.subst = subst

    def on_char(self, char):
        result = self.subst.get(char.char, None)
        return char if result is None else result


def replace(r: Regex[str], rules: Dict[str, Regex[str]]) -> Regex[str]:
    return r.fold(ReplaceHandler(rules))


TTransitionTable = Dict[Tuple[str, Optional[str]], Set[str]]


def _build_nfa_transitions(behavior: Iterable[Tuple[str, str]], start_events: List[str],
                           start_state="$START") -> TTransitionTable:
    """
    Build the NFA transition table given the device behavior and start events.
    How:
        - For each device behavior pair (src, dst), create an edge (src, dst, dst)
        - For each device start event, also create an edge (start_state, evt, evt)
        - For each edge, create key (src, char) and add value (dst)
    :param behavior: pairs of events that represent the device's macro event transitions
        Example: [('b.pressed', 'b.released'), ('b.released', 'b.pressed')]
    :param start_events: list of possible start events (requires len >= 1)
    :param start_state: reserved name for start state (must be different from all events)
    :return: table representing NFA transitions
    """

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

    return tsx


# XXX: make the start_state not be a string
def build_external_behavior(behavior: Iterable[Tuple[str, str]], start_events: List[str], events: List[str],
                            start_state="$START") -> NFA[Any, str]:
    """
    Build the external NFA that represents the device behavior (i.e., its macro event transitions)
    How:
        - For each device event, create an NFA accepted state with that name
        - Build the NFA transition table given the device behavior and start events

    :param behavior: pairs of events that represent the device's macro event transitions
        Example: [('b.pressed', 'b.released'), ('b.released', 'b.pressed')]
    :param start_events: list of possible start events (requires len >= 1)
    :param events: list of all device's events
    :param start_state: reserved name for start state (must be different from all events)
    :return: NFA representing the external behaviour
    """
    if len(start_events) == 0:
        raise ValueError("At least one start event must be specified.")

    if start_state in events:
        raise ValueError(f"Start state '{start_state}' cannot have the same name as an event.")

    # build NFA states
    states = set(evt for evt in events)
    states.add(start_state)

    # build NFA transitions
    tsx = _build_nfa_transitions(behavior, start_events, start_state)

    # create and return NFA
    return NFA(alphabet=frozenset(events),
               transition_func=NFA.transition_table(tsx),
               start_state=start_state,
               accepted_states=states)


def prefix_nfa(nfa: NFA, prefix: str) -> NFA:
    """
    The NFA definition of a device doesn't have a prefixed alphabet. However, when declaring components,
    we are referring to device instantiations (e.g., a device of type Button called 'buttonX'). Hence we need to prefix
    the alphabet on the NFA, so that we can, for example, refer to 'buttonX.pressed' transition instead of just 'pressed'.

    :param nfa: the NFA (device) we want to prefix with
    :param prefix: the instantiation name of the NFA (device) (e.g., 'Button b' with alphabet 'pressed' would became 'b.pressed')
    :return: prefixed NFA
    """
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


def build_components(components: Dict[str, str], known_devices: KnownDevices) -> Iterator[
    Tuple[str, NFA]]:
    """
    Build a structure of components that is a map of component name to device instance with a prefixed alphabet
    :func:`.prefix_nfa`

    :param components: map of component name to device type
        Example:  components = {"t": "Timer", "b": "Button"}

    :param known_devices: map of device type to device instance
        Example: known_devices = {"Timer": Timer(..started..timeout..), Button(..pressed..released..)} )

    :return: iterator of component name to device instance with alphabet prefixed with component name
        Example: "t": Timer(..t.started..t.timeout..), "b": Button(..b.pressed..b.released..)
    """
    for (name, ty) in components.items():
        yield name, prefix_nfa(known_devices[ty].nfa, name + ".")


def merge_components(components: Iterable[NFA[Any, str]], flatten: bool = False, minimize: bool = False) -> DFA[
    Any, str]:
    """
    Merge all components by using the shuffle operation
    :param components: list of components as NFAs (see :func:`.build_components`)
    :param flatten:
    :param minimize:
    :return: shuffled components DFA
    """
    # Get the first component
    dev, *rst = components

    # Shuffle all devices:
    for d in rst:
        dev = dev.shuffle(d)

    # Convert the given NFA into a minimized DFA #TODO: is this still valid?!
    dev_dfa = nfa_to_dfa(dev)

    if flatten:
        return dev_dfa.flatten(minimize=minimize)

    return dev_dfa


def encode_behavior(behavior: NFA[Any, str], triggers: Dict[str, Regex],
                    alphabet: Optional[Collection[str]] = None) -> NFA[Any, str]:
    assert isinstance(behavior, NFA)
    # Replace tokens by REGEX in encoder
    encoded_regex: Regex = replace(nfa_to_regex(behavior), triggers)
    return regex_to_nfa(encoded_regex, alphabet)


@dataclass(frozen=True, order=True)
class MacroState(DecodedState):
    state: AbstractSet[str]
    event: Optional[str] = None


@dataclass(frozen=True, order=True)
class MicroState(DecodedState):
    # The next macro state
    macro: AbstractSet[str]
    # The event that we are processing
    event: str
    # The current micro state
    micro: str

    def advance_micro(self, micro: str):
        return MicroState(macro=self.macro, event=self.event, micro=micro)

    def advance_macro(self):
        return MacroState(self.macro, self.event)


def is_macro_state(st):
    return isinstance(st, MacroState)


AmbiguousState = typing.Union[MicroState, MacroState]


def get_macro_states(st: AbstractSet[AmbiguousState]):
    return filter(is_macro_state, st)


def is_macro_ambiguous(st: AbstractSet[AmbiguousState]) -> bool:
    count = 0
    for _ in get_macro_states(st):
        count += 1
        if count > 1:
            return True
    return False


MacroTrace = Tuple[str, ...]
MicroTrace = Tuple[str, ...]


@dataclass
class AmbiguityFailure:
    micro_trace: MicroTrace
    macro_traces: Tuple[MacroTrace, MacroTrace]

    @classmethod
    def make(cls, micro_trace: MicroTrace, dfa: DFA[Any, str]):
        macro_traces = None
        rest = []
        seq = micro_trace
        for st in dfa.get_derivation(seq):
            sts = set(get_macro_states(st))
            if len(sts) == 1:
                m, = sts
                rest.append(m.event)
            elif len(sts) > 1:
                st1, st2, *st3 = sts
                head = tuple(rest)
                macro_traces = head + (st1.event,), head + (st2.event,)
                break
        if macro_traces is None:
            raise ValueError("Ambiguity expected")
        return cls(micro_trace, macro_traces)


@dataclass
class MicroBehavior:
    nfa: NFA[AmbiguousState, str]
    dfa: DFA[Any, str] = field(init=False)
    failure: Optional[AmbiguityFailure] = field(init=False)
    is_valid: bool = field(init=False)

    def __post_init__(self):
        self.dfa = nfa_to_dfa(self.nfa)
        err_trace = self.dfa.find_shortest_path(is_macro_ambiguous)
        self.is_valid = err_trace is None
        self.failure = None if self.is_valid else AmbiguityFailure.make(dfa=self.dfa, micro_trace=err_trace)

    def convert_micro_to_macro(self, seq: Iterable[str]) -> Tuple[MacroTrace, ...]:
        rest = [()]
        for st in self.dfa.get_derivation(seq):
            sts = set(get_macro_states(st))
            if len(sts) > 0:
                new_rest = list(
                    x + (st.event,) for x in rest
                    for st in sts
                )
                rest = new_rest
        return tuple(rest)

    @classmethod
    def make(cls, external_behavior: NFA[Any, str], triggers: Dict[str, Regex[str]],
             alphabet: Optional[Collection[str]] = None) -> "MicroBehavior":
        """
        Encode behavior
        
        How:
            - convert external behavior (NFA) and triggers (REGEX) to DFAs (because ... ???)
            -
        :param external_behavior: device external behavior as NFA
        :param triggers: device triggers as REGEX
        :param alphabet: the alphabet from all shuffled components (should be equivalent to the alphabet from all triggers)
        :return:
        """
        assert isinstance(external_behavior, NFA)
        det_behavior: DFA[AbstractSet[str], str] = nfa_to_dfa(external_behavior)
        det_triggers = dict((k, nfa_to_dfa(regex_to_nfa(v))) for k, v in triggers.items())
        # det_triggers and triggers are so close together, make sure we don't mistype
        del triggers
        # make sure we don't use external_behavior in the rest of the code
        del external_behavior

        def tsx(src, char):
            if isinstance(src, MacroState):
                if char is not None:
                    return frozenset()
                # Macro-state
                result = set()
                for evt in det_behavior.alphabet:
                    result.add(MicroState(
                        macro=det_behavior.transition_func(src.state, evt),
                        event=evt,
                        micro=det_triggers[evt].start_state
                    ))
                return frozenset(result)
            elif isinstance(src, MicroState):
                dfa = det_triggers[src.event]
                if dfa.accepted_states(src.micro) and char is None:
                    return frozenset([src.advance_macro()])
                elif char in dfa.alphabet:
                    dst = src.advance_micro(dfa.transition_func(src.micro, char))
                    return frozenset([dst])
                return frozenset()
            else:
                raise ValueError("Unknown state", src, char)

        def is_final(st):
            return isinstance(st, MacroState) and det_behavior.accepted_states(st.state)

        if alphabet is None:
            # Infer the alphabet from each trigger
            alphabet = set()
            for dfa in det_triggers.values():
                alphabet.update(dfa.alphabet)

        nfa = NFA[typing.Union[MacroState, MicroState], str](
            alphabet=alphabet,
            transition_func=tsx,
            start_state=MacroState(det_behavior.start_state),
            accepted_states=is_final
        )
        return cls(nfa)


@dataclass
class TriggerIntegrationFailure:
    micro_trace: MicroTrace
    macro_trace: MacroTrace
    component_errors: Dict[str, Tuple[MacroTrace, int]]

    @classmethod
    def make(cls, micro: MicroBehavior, dfa: [Any, str], known_devices: KnownDevices,
             components: Dict[str, str]) -> "TriggerIntegrationFailure":
        # We could not assemble the device
        # We compute the smallest error
        dec_seq: Optional[MicroTrace] = dfa.get_shortest_string()
        assert dec_seq is not None, "dec_seq can only be none if failure is empty, which cannot be"
        # There should be a unique macro trace
        macro_trace, = micro.convert_micro_to_macro(dec_seq)
        # We demutex by device
        errs = dict()
        for component, seq in demultiplex(dec_seq).items():
            ch_dev = known_devices[components[component]]
            if not ch_dev.nfa.accepts(seq):
                dfa = nfa_to_dfa(ch_dev.nfa).minimize()
                idx = dfa.get_divergence_index(seq)
                assert idx is not None, "The index can only be None if the behavior is empty, which should never happen"
                errs[component] = (tuple(seq), idx)

        return cls(dec_seq, macro_trace, errs)


@dataclass
class AssembledMicroBehavior:
    possible: DFA[Any, str]
    impossible: DFA[Any, str]
    micro: MicroBehavior
    is_valid: bool = field(init=False)

    def __post_init__(self):
        self.is_valid = self.micro.is_valid and self.impossible.is_empty()

    @property
    def dfa(self) -> DFA[Any, str]:
        return self.micro.dfa

    @property
    def nfa(self) -> NFA[AmbiguousState, str]:
        return self.micro.nfa

    def get_failure(self, known_devices: KnownDevices, components: Dict[str, str]):
        # Fill in the failure field
        failure = self.micro.failure
        if failure is None and not self.impossible.is_empty():
            failure = TriggerIntegrationFailure.make(self.micro, self.impossible, known_devices, components)
        return failure

    @classmethod
    def make(cls, components: List[NFA[Any, str]], external_behavior: NFA[Any, str],
             triggers: Dict[str, Regex[str]],
             minimize=False, flatten=False) -> "AssembledMicroBehavior":
        """
        Build internal behavior by using components, external behavior and triggers
        How:
            - Shuffle all components into a minimized DFA (minimized because ... ??? )
            -
        :param components: list of components as NFAs
        :param external_behavior: device external behavior as NFA
        :param triggers: device triggers as REGEX
            Example:
        :param minimize:
        :param flatten:
        """
        if len(components) == 0:
            raise ValueError("Should not be creating an internal behavior with 0 components")

        all_possible: DFA[Any, str] = merge_components(components, flatten, minimize)  # shuffle operation

        internal_behavior = MicroBehavior.make(external_behavior, triggers, all_possible.alphabet)
        # Ensure that the all possible behaviors in dev contain the encoded behavior
        invalid_behavior = internal_behavior.dfa.subtract(all_possible)
        # Ready to create the object
        return cls(
            possible=all_possible,
            impossible=invalid_behavior,
            micro=internal_behavior,
        )


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


def demultiplex(seq: Iterable[str]) -> Mapping[str, List[str]]:
    sequences: Dict[str, List[str]] = dict()
    for msg in seq:
        component, op = msg.split(".")
        component_seq = sequences.get(component, None)
        if component_seq is None:
            sequences[component] = component_seq = []
        component_seq.append(op)
    return sequences


FormulaOrTrace = typing.Union[List[str], hml.Formula[str]]


def parse_formula(data: Any) -> FormulaOrTrace:
    if isinstance(data, list):
        return typing.cast(List[str], data)
    return hml.Formula.deserialize(data)


def check_traces(mc: Callable[[FormulaOrTrace], bool], tests: Mapping[str, Mapping[str, Any]]) -> None:
    for key, trace in tests.get('ok', dict()).items():
        formula = parse_formula(trace)
        if not mc(formula):
            raise ValueError(f"Unaccepted valid trace: {key}: {trace}")

    for key, trace in tests.get('fail', dict()).items():
        if mc(parse_formula(trace)):
            raise ValueError(f"Unexpected invalid trace: {key}: {trace}")


def model_check(nfa: NFA[Any, str], word_or_formula: typing.Union[List[str], hml.Formula[str]]) -> bool:
    if isinstance(word_or_formula, list):
        return nfa.accepts(word_or_formula)
    else:
        prop = nfa_to_dfa(word_or_formula.interpret(nfa.alphabet))
        model = nfa_to_dfa(nfa)
        return not prop.intersection(model).is_empty()


@dataclass
class AssembledDevice:
    external: CheckedDevice
    internal: AssembledMicroBehavior
    is_valid: bool = field(init=False)
    failure: Optional[typing.Union[AmbiguityFailure, TriggerIntegrationFailure]]

    def __post_init__(self):
        self.is_valid = self.failure is None

    def internal_model_check(self, word_or_formula: typing.Union[List[str], hml.Formula[str]]) -> bool:
        return model_check(self.internal.nfa, word_or_formula)

    def external_model_check(self, word_or_formula: typing.Union[List[str], hml.Formula[str]]):
        return model_check(self.external.nfa, word_or_formula)

    @classmethod
    def make(cls, dev: Device, known_devices: Mapping[str, CheckedDevice]) -> "AssembledDevice":
        """
        In order to assemble a device, the following steps are required:
        * ensure well formedness (start_evts <= evts, trigs <= evts, and trigs == evts)
        * compute the external behavior
        * compute the list of components with prefixed NFAs
        * compute the internal behavior using the external behavior, components, and triggers

        :param dev: the device to be assembled
        :param known_devices: map of device type to checked device instance (NFA)
        :return:
        """
        ensure_well_formed(dev)
        external_behavior: NFA = build_external_behavior(dev.behavior, dev.start_events, dev.events)
        ext = CheckedDevice(external_behavior)
        micro = None
        fail = None
        if len(dev.components) > 0:
            # Since there are components, we must assemble them
            components_behaviors: List[NFA] = list(dict(build_components(dev.components, known_devices)).values())
            micro = AssembledMicroBehavior.make(
                components=components_behaviors,
                external_behavior=external_behavior,
                triggers=dev.triggers
            )
            fail = micro.get_failure(known_devices, dev.components)

        return cls(external=ext, internal=micro, failure=fail)
