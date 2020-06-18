from typing import (
    List,
    Dict,
    Iterable,
    Tuple,
    Any,
    Optional,
    Collection,
    Mapping,
    Set,
    Iterator,
    Callable,
    AbstractSet,
    Union,
    cast,
    TypeVar,
    FrozenSet,
    Sequence,
)
from karakuri.regular import (
    NFA,
    nfa_to_regex,
    regex_to_nfa,
    Regex,
    nfa_to_dfa,
    dfa_to_nfa,
    DFA,
    SubstHandler,
)
from dataclasses import dataclass, field
from karakuri import hml, regular
from contextlib import contextmanager

# https://stackoverflow.com/questions/7370801/measure-time-elapsed-in-python
from timeit import default_timer as timer
from datetime import timedelta


def get_elapsed_time(start: float) -> timedelta:
    return timedelta(seconds=timer() - start)


@dataclass
class Device:
    start_events: List[str]
    final_events: List[str]
    events: List[str]
    behavior: List[Tuple[str, str]]
    components: Dict[str, str]
    triggers: Dict[str, Regex]


@dataclass
class CheckedDevice:
    nfa: NFA[Any, str]


TKnownDevices = Callable[[str], CheckedDevice]


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


TNFATransitions = Dict[Tuple[str, Optional[str]], Set[str]]


def _build_nfa_transitions(
    behavior: Iterable[Tuple[str, str]],
    start_events: List[str],
    start_state: str = "$START",
) -> TNFATransitions:
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
def build_external_behavior(
    behavior: Iterable[Tuple[str, str]],
    start_events: List[str],
    final_events: List[str],
    events: List[str],
    start_state: str = "$START",
) -> NFA[Any, str]:
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

    if len(final_events) == 0:
        raise ValueError("At least one final event must be specified.")

    if start_state in events:
        raise ValueError(
            f"Start state '{start_state}' cannot have the same name as an event."
        )

    # build NFA accepted states
    accepted_states: Set[str] = set(final_events)

    # build NFA transitions (arcs)
    tsx: TNFATransitions = _build_nfa_transitions(behavior, start_events, start_state)

    # create and return NFA
    return NFA(
        alphabet=frozenset(events),
        transition_func=NFA.transition_table(tsx),
        start_state=start_state,
        accepted_states=accepted_states,
    )


def instantiate(nfa: NFA, prefix: str) -> NFA:
    """
    The NFA definition of a device doesn't have a prefixed alphabet. However, when declaring components,
    we are referring to device instantiations (e.g., a device of type Button called 'buttonX').
    Hence we need to prefix the alphabet on the NFA, so that we can, for example, refer to
    'buttonX.pressed' transition instead of just 'pressed'.

    :param nfa: the NFA (device) we want to prefix with
    :param prefix: the instantiation name of the NFA (device)
    (e.g., 'Button b' with alphabet 'pressed' would became 'b.pressed')
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
        accepted_states=nfa.accepted_states,
    )


@dataclass
class Component:
    name: str
    system: CheckedDevice
    behavior: NFA[Any, str] = field(init=False)

    @property
    def alphabet(self):
        return self.behavior.alphabet

    def __post_init__(self):
        self.behavior = instantiate(self.system.nfa, self.name + ".")


def shuffle(nfas: Iterable[NFA[Any, str]]) -> NFA[Any, str]:
    # Get the first component
    result, *rst = nfas

    # Shuffle all devices:
    for d in rst:
        result = result.shuffle(d)
    return result


def encode_behavior(
    behavior: NFA[Any, str],
    triggers: Dict[str, Regex],
    alphabet: Optional[Collection[str]] = None,
) -> NFA[Any, str]:
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
    micro: AbstractSet[str]

    def advance_micro(self, micro: AbstractSet[str]) -> "MicroState":
        return MicroState(macro=self.macro, event=self.event, micro=micro)

    def advance_macro(self) -> MacroState:
        return MacroState(self.macro, self.event)


def is_macro_state(st) -> bool:
    return isinstance(st, MacroState)


def is_macro_ambiguous(st: AbstractSet[DecodedState]) -> bool:
    count = 0
    for _ in filter(is_macro_state, st):
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
    def make(cls, micro_trace: MicroTrace, dfa: DFA[Any, str]) -> "AmbiguityFailure":
        macro_traces = None
        rest = []
        seq = micro_trace
        for st in dfa.get_derivation(seq):
            sts = set(filter(is_macro_state, st))
            if len(sts) == 1:
                (m,) = sts
                rest.append(m.event)
            elif len(sts) > 1:
                st1, st2, *st3 = sts
                head = tuple(rest)
                macro_traces = head + (st1.event,), head + (st2.event,)
                break
        if macro_traces is None:
            raise ValueError("Ambiguity expected")
        return cls(micro_trace, macro_traces)


S = TypeVar("S")
A = TypeVar("A")


def project_nfa(nfa: NFA[S, A], alphabet: Collection[A]) -> NFA[S, A]:
    old_tsx = nfa.transition_func
    remaining = set(nfa.alphabet)
    remaining.difference_update(alphabet)

    def tsx(st, char):
        if char is None:
            result = set()
            for other_char in remaining:
                result.update(old_tsx(st, other_char))
            result.update(old_tsx(st, None))
            return result
        elif char in alphabet:
            return old_tsx(st, char)
        else:
            return frozenset()

    return NFA(
        alphabet=alphabet,
        transition_func=tsx,
        start_state=nfa.start_state,
        accepted_states=nfa.accepted_states,
    )


def pad_trace(trace: Tuple[A, ...], alphabet: Collection[A]) -> NFA[Any, A]:
    """
    Given a trace and some padding characters, returns the set of all
    strings that interleave padding characters in the given trace.

    For instance, if trace=[a,b] and alphabet=[c], then examples of padded
    strings are:
    - acb
    - ab
    - ccccacccbccc
    """

    def tsx(st: int, letter: Optional[A]) -> FrozenSet[int]:
        if letter in alphabet:
            return frozenset([st])
        if st < len(trace) and letter == trace[st]:
            return frozenset([st + 1])
        return frozenset()

    target_alphabet = set(alphabet)
    target_alphabet.update(trace)
    return NFA(
        alphabet=target_alphabet,
        transition_func=tsx,
        start_state=0,
        accepted_states=[len(trace)],
    )


@dataclass
class MicroBehavior:
    nfa: NFA[DecodedState, str]
    system: NFA[Any, str]
    dfa: DFA[Any, str] = field(init=False)
    failure: Optional[AmbiguityFailure] = field(init=False)
    is_valid: bool = field(init=False)
    validation_time: timedelta = field(init=False)

    def __post_init__(self) -> None:
        start = timer()
        self.dfa = nfa_to_dfa(self.nfa)
        err_trace = self.dfa.find_shortest_path(is_macro_ambiguous)
        self.is_valid = err_trace is None
        self.failure = (
            None
            if err_trace is None  # is valid
            else AmbiguityFailure.make(dfa=self.dfa, micro_trace=err_trace)
        )
        self.validation_time = get_elapsed_time(start)

    def convert_micro_to_macro(self, seq: Sequence[str]) -> MacroTrace:
        for der in self.nfa.get_derivations(seq):
            rest: List[str] = []
            for st in der:
                if isinstance(st, MacroState) and st.event is not None:
                    rest.append(st.event)
            # Some traces have no macro traces; and this would be an invalid
            # trace. We therefore need to ensure the found macro-trace exists
            if rest in self.system:
                return tuple(rest)
        raise ValueError(f"Sequence {seq} yields 0 derivations!")

    def get_traces_from_component_trace(
        self, component_alpha: Collection[str], component_seq: MicroTrace
    ) -> DFA[Any, str]:
        # 1. Compute the set of characters to pad
        pad_alpha = set(self.dfa.alphabet)
        pad_alpha.difference_update(component_alpha)
        # 2. Find the set of all padded strings
        trace_dfa = nfa_to_dfa(pad_trace(trace=component_seq, alphabet=pad_alpha))
        # 3. Find the set of padded strings that are in the micro
        return self.dfa.intersection(trace_dfa.set_alphabet(self.dfa.alphabet))

    @classmethod
    def make(
        cls,
        external_behavior: NFA[Any, str],
        triggers: Dict[str, Regex[str]],
        alphabet: Set[str],
    ) -> "MicroBehavior":
        """
        Micro behavior

        How:
            - convert external behavior (NFA) and triggers (REGEX) to DFA (needed for ambiguity)
            -
        :param external_behavior: device external behavior as NFA
        :param triggers: device triggers as REGEX
        :param alphabet: the alphabet from all shuffled components
        (should be equivalent to the alphabet from all triggers)
        :return:
        """
        assert isinstance(external_behavior, NFA)
        det_triggers: Dict[str, DFA[Any, str]] = dict()
        for k, rule in triggers.items():
            rule_alpha = set(regular.get_alphabet(rule))
            rule_alpha = rule_alpha - alphabet
            if len(rule_alpha) > 0:
                raise ValueError(f"Operation '{k}': unknown operations {rule_alpha}")
            det_triggers[k] = nfa_to_dfa(regex_to_nfa(rule, alphabet))
        # det_triggers and triggers are so close together, make sure we don't mistype
        del triggers

        def tsx(src: DecodedState, char: Optional[str]) -> AbstractSet[DecodedState]:
            if isinstance(src, MacroState):
                if char is not None:
                    return frozenset()
                # Macro-state
                result = set()
                for evt in external_behavior.alphabet:
                    for dst in external_behavior.transition_func(src.state, evt):
                        result.add(
                            MicroState(
                                macro=dst,
                                event=evt,
                                micro=det_triggers[evt].start_state,
                            )
                        )
                return frozenset(result)
            elif isinstance(src, MicroState):
                dfa = det_triggers[src.event]
                if dfa.accepted_states(src.micro) and char is None:
                    return frozenset([src.advance_macro()])
                elif char in dfa.alphabet:
                    assert char is not None
                    dst = src.advance_micro(dfa.transition_func(src.micro, char))
                    return frozenset([dst])
                return frozenset()
            else:
                raise ValueError("Unknown state", src, char)

        def is_final(st) -> bool:
            return isinstance(st, MacroState) and external_behavior.accepted_states(
                st.state
            )

        if alphabet is None:
            # Infer the alphabet from each trigger
            alphabet = set()
            for t_dfa in det_triggers.values():
                alphabet.update(t_dfa.alphabet)

        nfa = NFA[DecodedState, str](
            alphabet=alphabet,
            transition_func=tsx,
            start_state=MacroState(external_behavior.start_state),
            accepted_states=is_final,
        )
        return cls(nfa, external_behavior)


@dataclass
class ComponentUsage:
    projected: DFA[Any, str]
    component: DFA[Any, str]
    is_valid: bool = field(init=False)
    validation_time: timedelta = field(init=False)

    def __post_init__(self) -> None:
        start = timer()
        self.is_valid = self.component.contains(self.projected)
        self.validation_time = get_elapsed_time(start)

    def __equals__(self, other: Any) -> bool:
        if other is None or not isinstance(other, ComponentUsage):
            return False
        return self.projected == other.projected and self.component == other.component

    def is_equivalent_to(self, other: "ComponentUsage") -> bool:
        return self.projected.is_equivalent_to(
            other.projected
        ) and self.component.is_equivalent_to(other.component)

    @property
    def invalid(self) -> DFA[Any, str]:
        """Returns the set of invalid traces."""
        return self.projected.subtract(self.component)

    def get_smallest_error(self) -> MicroTrace:
        """
        Returns the smallest error issued by this component's usage.
        """
        if self.is_valid:
            raise ValueError("Can only be called if projection is invalid.")
        # 2. Get the shortest string therein
        component_seq: Optional[MicroTrace] = self.invalid.get_shortest_string()
        assert component_seq is not None
        return component_seq

    @classmethod
    def make(
        cls, micro: NFA[Any, str], component: NFA[Any, str], optional: bool = True
    ) -> "ComponentUsage":
        """
        Restrict the language of a micro behavior using a component's alphabet
        """
        projected: DFA[Any, str] = nfa_to_dfa(project_nfa(micro, component.alphabet))
        if optional:
            nil = DFA[Any, str].make_nil(projected.alphabet)
            projected = projected.subtract(nil)

        return cls(component=nfa_to_dfa(component), projected=projected,)


@dataclass
class TriggerIntegrationFailure:
    micro_trace: MicroTrace
    macro_trace: MacroTrace
    component_errors: Dict[str, Tuple[MacroTrace, int]]

    def component_to_micro(self, component: str, macro_trace: MacroTrace) -> int:
        ops = tuple(component + "." + op for op in macro_trace)
        idx = 0
        for micro_idx, x in enumerate(self.micro_trace):
            if x == ops[idx]:
                idx += 1
                if idx == len(ops):
                    return micro_idx
        raise ValueError(f"Unknown: {component} {macro_trace}")

    def _str_trace(self, lbl, trace, errs):
        elems = []
        for idx, op in enumerate(trace):
            if idx in errs:
                elems.append("^" * len(op))
            else:
                elems.append(" " * len(op))
        micro = lbl + ", ".join(trace)
        highlight = " " * len(lbl) + "  ".join(elems)
        return micro, highlight

    def __str__(self):
        base = repr(self)
        micro_idx = set()
        for name, (macro_trace, idx) in self.component_errors.items():
            micro_idx.add(self.component_to_micro(name, macro_trace[0 : idx + 1]))
        # result = "Error trace: "
        macro = "* system: " + ", ".join(self.macro_trace)
        micro, micro_hl = self._str_trace(
            "* integration: ", self.micro_trace, micro_idx
        )
        lines = []
        for name, (macro_trace, err_idx) in sorted(
            self.component_errors.items(), key=lambda x: x[0]
        ):
            trace, trace_hl = self._str_trace(
                lbl=f"  {name!r}: ", trace=macro_trace, errs={err_idx,},
            )
            lines.append(trace)
            lines.append(trace_hl)
        err = "\n".join(lines)
        return f"integration error\n\n{macro}\n{micro}\n{micro_hl}\nInstance errors:\n\n{err}"

    @classmethod
    def make(
        cls,
        micro: MicroBehavior,
        invalid: DFA[Any, str],
        known_devices: TKnownDevices,
        components: Dict[str, str],
    ) -> "TriggerIntegrationFailure":
        # We could not assemble the device
        # We compute the smallest error
        dec_seq: Optional[MicroTrace] = invalid.get_shortest_string()
        assert (
            dec_seq is not None
        ), "dec_seq can only be none if failure is empty, which cannot be"
        # There should be a unique macro trace
        macro_trace = micro.convert_micro_to_macro(dec_seq)
        # We demutex by device
        errs = dict()
        for component, seq in demultiplex(dec_seq).items():
            ch_dev = known_devices(components[component])
            if not ch_dev.nfa.accepts(seq):
                invalid = nfa_to_dfa(ch_dev.nfa).minimize()
                idx = invalid.get_divergence_index(seq)
                assert (
                    idx is not None
                ), "The index can only be None if the behavior is empty, which should never happen"
                errs[component] = (tuple(seq), idx)

        return cls(dec_seq, macro_trace, errs)

    @classmethod
    def from_component_usage(
        cls,
        component: str,
        usage: ComponentUsage,
        micro: MicroBehavior,
        known_devices: TKnownDevices,
        components: Dict[str, str],
    ) -> "TriggerIntegrationFailure":
        if usage.is_valid:
            raise ValueError(f"Expecting an invalid projection, but got: {usage}")
        # 1. Get an invalid usage
        component_seq = usage.get_smallest_error()
        # 2. Get the component's alphabet
        component_alpha = set(
            component + "." + x
            for x in known_devices(components[component]).nfa.alphabet
        )
        # 3. Get the set of invalid traces
        invalid = micro.get_traces_from_component_trace(component_alpha, component_seq)
        return cls.make(
            micro=micro,
            invalid=invalid,
            known_devices=known_devices,
            components=components,
        )


@dataclass
class UnusableOperationsFailure:
    unusable_operations: FrozenSet[str]
    sink_operations: FrozenSet[str]

    def __str__(self):
        return f"Unusable operation error\nUnreachable operations: {', '.join(self.unusable_operations)}\nThese operations do not reach a yield point: {', '.join(self.sink_operations)}"


TFailure = Union[TriggerIntegrationFailure, AmbiguityFailure, UnusableOperationsFailure]


@dataclass
class AssembledMicroBehavior2:
    usages: Dict[str, ComponentUsage]
    micro: MicroBehavior
    is_valid: bool = field(init=False)
    validation_time: timedelta = field(init=False)

    def __post_init__(self) -> None:
        invalid_count = 0
        self.validation_time = timedelta()
        for x in self.usages.values():
            if not x.is_valid:
                invalid_count += 1
            self.validation_time += x.validation_time
        self.is_valid = invalid_count == 0

    @property
    def dfa(self) -> DFA[Any, str]:
        return self.micro.dfa

    @property
    def nfa(self) -> NFA[DecodedState, str]:
        return self.micro.nfa

    def get_failure(
        self, known_devices: TKnownDevices, components: Dict[str, str]
    ) -> Optional[TFailure]:
        # Fill in the failure field
        failure: Optional[TFailure] = self.micro.failure
        if failure is None and not self.is_valid:
            for (cid, usage) in self.usages.items():
                if not usage.is_valid:
                    return TriggerIntegrationFailure.from_component_usage(
                        component=cid,
                        usage=usage,
                        micro=self.micro,
                        known_devices=known_devices,
                        components=components,
                    )
        return failure

    @classmethod
    def make(
        cls,
        components: Dict[str, Component],
        external_behavior: NFA[Any, str],
        triggers: Dict[str, Regex[str]],
    ) -> "AssembledMicroBehavior2":
        if len(components) == 0:
            raise ValueError(
                "Should not be creating an internal behavior with 0 components"
            )
        alphabet: Set[str] = set()
        for c in components.values():
            alphabet.update(c.alphabet)
        micro = MicroBehavior.make(external_behavior, triggers, alphabet)
        usages = dict(
            (
                (k, ComponentUsage.make(micro=micro.nfa, component=c.behavior))
                for k, c in components.items()
            )
        )
        return cls(usages=usages, micro=micro)


@dataclass
class AssembledMicroBehavior:
    possible: DFA[Any, str]
    impossible: DFA[Any, str]
    micro: MicroBehavior
    is_valid: bool = field(init=False)
    validation_time: timedelta = field(init=False)

    def __post_init__(self) -> None:
        start = timer()
        self.is_valid = self.micro.is_valid and self.impossible.is_empty()
        self.validation_time = get_elapsed_time(start)

    @property
    def dfa(self) -> DFA[Any, str]:
        return self.micro.dfa

    @property
    def nfa(self) -> NFA[DecodedState, str]:
        return self.micro.nfa

    def get_failure(
        self, known_devices: TKnownDevices, components: Dict[str, str]
    ) -> Optional[TFailure]:
        # Fill in the failure field
        failure: Optional[TFailure] = self.micro.failure
        if failure is None and not self.is_valid:
            failure = TriggerIntegrationFailure.make(
                self.micro, self.impossible, known_devices, components
            )
        return failure

    @classmethod
    def make(
        cls,
        components: List[Component],
        external_behavior: NFA[Any, str],
        triggers: Dict[str, Regex[str]],
    ) -> "AssembledMicroBehavior":
        """
        Build internal behavior by using components, external behavior and triggers
        How:
            - Shuffle all components into a minimized DFA (minimized because ... ??? )
            -
        :param components: list of components as NFAs
        :param external_behavior: device external behavior as NFA
        :param triggers: device triggers as REGEX
            Example:
        """
        if len(components) == 0:
            raise ValueError(
                "Should not be creating an internal behavior with 0 components"
            )

        all_possible: DFA[Any, str] = nfa_to_dfa(
            shuffle(c.behavior for c in components)
        )

        internal_behavior = MicroBehavior.make(
            external_behavior, triggers, set(all_possible.alphabet)
        )
        # Ensure that the all possible behaviors in dev contain the encoded behavior
        invalid_behavior = internal_behavior.dfa.subtract(all_possible)
        # Ready to create the object
        return cls(
            possible=all_possible, impossible=invalid_behavior, micro=internal_behavior,
        )


def ensure_well_formed(dev: Device) -> None:
    evts = set(dev.events)
    start_evts = set(dev.start_events)
    if not (start_evts <= evts):
        raise ValueError(
            "start_events must be included in events, got these extra: ",
            start_evts - evts,
        )
    # Get keys
    trigs = set(dev.triggers)
    if not (trigs <= evts):
        raise ValueError(
            "All events must be defined in triggers. These triggers are undefined events: ",
            trigs - evts,
        )
    if trigs != evts:
        raise ValueError("The following trigger rules were not defined: ", evts - trigs)


def demultiplex(seq: Iterable[str]) -> Mapping[str, List[str]]:
    sequences: Dict[str, List[str]] = dict()
    for msg in seq:
        component, op = msg.split(".")
        component_seq = sequences.get(component, None)
        if component_seq is None:
            sequences[component] = component_seq = []
        component_seq.append(op)
    return sequences


FormulaOrTrace = Union[List[str], hml.Formula[str]]


def parse_formula(data: Any) -> FormulaOrTrace:
    if isinstance(data, list):
        return cast(List[str], data)
    return hml.Formula.deserialize(data)


def check_traces(
    mc: Callable[[FormulaOrTrace], bool], tests: Mapping[str, Mapping[str, Any]]
) -> None:
    for key, trace in tests.get("ok", dict()).items():
        formula = parse_formula(trace)
        if not mc(formula):
            raise ValueError(f"Unaccepted valid trace '{key}': {trace}")

    for key, trace in tests.get("fail", dict()).items():
        if mc(parse_formula(trace)):
            raise ValueError(f"Unexpected invalid trace '{key}': {trace}")


def model_check(
    nfa: NFA[Any, str], word_or_formula: Union[List[str], hml.Formula[str]]
) -> bool:

    if isinstance(word_or_formula, list):
        for string in word_or_formula:
            if string not in nfa.alphabet:
                raise ValueError(f"Undeclared event in trace: '{string}'")
        return nfa.accepts(word_or_formula)
    else:
        prop = nfa_to_dfa(word_or_formula.interpret(nfa.alphabet))
        model = nfa_to_dfa(nfa)
        return not prop.intersection(model).is_empty()


@dataclass(frozen=True)
class Timings:
    ambiguity_check_time: Optional[timedelta]
    integration_check_time: Optional[timedelta]
    unusable_operations_time: timedelta
    total_check_time: timedelta = field(init=False)

    def __post_init__(self):
        t1 = (
            timedelta(0)
            if self.ambiguity_check_time is None
            else self.ambiguity_check_time
        )
        t2 = (
            timedelta(0)
            if self.integration_check_time is None
            else self.integration_check_time
        )
        object.__setattr__(
            self, "total_check_time", t1 + t2 + self.unusable_operations_time
        )


@dataclass
class AssembledDevice:
    external: CheckedDevice
    internal: Optional[Union[AssembledMicroBehavior, AssembledMicroBehavior2]]
    failure: Optional[TFailure]
    operations: FrozenSet[str]
    is_valid: bool = field(init=False)
    sink_operations: FrozenSet[str] = field(init=False)
    unusable_operations: FrozenSet[str] = field(init=False)
    unusable_operations_time: timedelta = field(init=False)

    def __post_init__(self):
        # Calculate unreachable and sink ops:
        start = timer()

        # only includes states that are reachable (and remove start)
        all_states = set(self.external.nfa.states)
        all_states.remove(self.external.nfa.start_state)

        # only includes states that are reachable and not sink (and remove start)
        all_states_without_sink = set(self.external.nfa.remove_sink_states().states)
        all_states_without_sink.remove(self.external.nfa.start_state)

        # collect unreachable operations
        self.unusable_operations = frozenset(set(self.operations) - all_states)

        # collect sink operations (does not include unreachable states!)
        self.sink_operations = frozenset(all_states - all_states_without_sink)

        self.unusable_operations_time = get_elapsed_time(start)

        if self.failure is None:
            if len(self.unusable_operations) > 0 or len(self.sink_operations) > 0:
                self.failure = UnusableOperationsFailure(
                    self.unusable_operations, self.sink_operations
                )
        # End of unreachable ops
        self.is_valid = self.failure is None

    def get_timings(self) -> Timings:
        return Timings(
            ambiguity_check_time=None
            if self.internal is None or self.internal.micro is None
            else self.internal.micro.validation_time,
            integration_check_time=None
            if self.internal is None
            else self.internal.validation_time,
            unusable_operations_time=self.unusable_operations_time,
        )

    def internal_model_check(
        self, word_or_formula: Union[List[str], hml.Formula[str]]
    ) -> bool:
        if self.internal is None:
            raise ValueError(
                "Cannot call internal_model_checker if there is no internal behavior"
            )
        return model_check(self.internal.nfa, word_or_formula)

    def external_model_check(self, word_or_formula: Union[List[str], hml.Formula[str]]):
        return model_check(self.external.nfa, word_or_formula)

    @classmethod
    def make(
        cls, dev: Device, known_devices: TKnownDevices, fast_check: bool = False,
    ) -> "AssembledDevice":
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
        external_behavior: NFA = build_external_behavior(
            dev.behavior, dev.start_events, dev.final_events, dev.events
        )
        ext = CheckedDevice(external_behavior)
        micro: Optional[Union[AssembledMicroBehavior, AssembledMicroBehavior2]] = None
        fail = None
        if len(dev.components) > 0:
            # Load the map of components
            components: Dict[str, Component] = dict(
                (name, Component(name, known_devices(ty)))
                for (name, ty) in dev.components.items()
            )
            if fast_check:
                micro = AssembledMicroBehavior2.make(
                    components=components,
                    external_behavior=external_behavior,
                    triggers=dev.triggers,
                )
            else:
                micro = AssembledMicroBehavior.make(
                    components=list(components.values()),
                    external_behavior=external_behavior,
                    triggers=dev.triggers,
                )
            fail = micro.get_failure(known_devices, dev.components)

        return cls(
            external=ext, internal=micro, failure=fail, operations=frozenset(dev.events)
        )
