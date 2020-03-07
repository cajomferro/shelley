from dfaapp.automaton import NFA, tag, render_dfa, render_nfa


class Regex:
    pass


class Char(Regex):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return str(self.char)

    def __eq__(self, other):
        return isinstance(other, Char) and self.char == other.char

    def __hash__(self):
        return hash(self.char)


class Empty(Regex):
    def __repr__(self):
        return u"[]"

    def __hash__(self):
        return hash(self.__class__)


Empty = Empty()


class Nil(Regex):
    def __repr__(self):
        return "{}"

    def __hash__(self):
        return hash(self.__class__)


Nil = Nil()


def is_primitive(r):
    if isinstance(r, Concat) and is_primitive(r.left) and is_primitive(
            r.right):
        return True
    if isinstance(r, Star) and isinstance(r.child, Char):
        return True
    return r is Nil or r is Empty or isinstance(r, Char)


def paren(r):
    text = repr(r)
    return text if is_primitive(r) else f"({text})"


class Concat(Regex):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self._data = (left, right)

    def __repr__(self):
        return f"{paren(self.left)}{paren(self.right)}"

    def as_tuple(self):
        return self._data

    def __hash__(self):
        return hash(self._data)

    def __eq__(self, other):
        return isinstance(other, Concat) and self._data == other._data

    @staticmethod
    def from_list(args):
        result = Empty
        for elem in args:
            result = concat(result, elem)
        return result


def concat(left, right):
    if left is Empty:
        return right
    if right is Empty:
        return left
    if right is Nil or left is Nil:
        return Nil
    return Concat(left, right)


class Union(Regex):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self._data = (left, right)

    def __repr__(self):
        if isinstance(self.left, Union) and isinstance(self.right, Union):
            return f"{self.left} + {self.right}"

        if isinstance(self.left, Union):
            return f"{self.left} + {paren(self.right)}"

        if isinstance(self.right, Union):
            return f"{paren(self.left)} + {self.right}"

        return f"{paren(self.left)} + {paren(self.right)}"

    def __hash__(self):
        return hash(self._data)

    def as_tuple(self):
        return self._data

    def flatten(n):
        result = set()
        to_visit = [n]
        while len(to_visit) > 0:
            n = to_visit.pop()
            if isinstance(n, Union):
                to_visit.extend(n.as_tuple())
            elif n is not Nil:
                result.add(n)
        return result

    def __eq__(self, other):
        return isinstance(other, Union) and self._data == other._data

    @classmethod
    def from_list(cls, iterable):
        result = None
        for x in iterable:
            if result is None:
                result = x
            else:
                result = cls(x, result)
        return result


def union(left, right):
    if left is Nil:
        return right
    if right is Nil:
        return left
    if isinstance(right, Star):
        if left is Empty:
            return right
    if isinstance(left, Star):
        if right is Empty:
            return left
    return Union.from_list(Union(left, right).flatten())


def op_and(c1, c2):
    return Union(concat(c1, c2), concat(c2, c1))


class Star(Regex):
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"{paren(self.child)}*"


def star(child):
    if child is Empty:
        return Empty
    if child is Nil:
        return Empty
    return Star(child)


def wrap(nfa):
    start = (0, 0)
    end = (0, 1)
    #states = set(tag(1, nfa.states))
    #states.add(start)
    #states.add(end)

    def tsx(st, a):
        if st is start:
            return frozenset({(1, nfa.start_state)
                              }) if a is None else frozenset()
        if st is end:
            return frozenset()
        idx, st = st
        assert idx == 1
        rest = frozenset(tag(1, nfa.transition_func(st, a)))
        if nfa.accepted_states(st) and a is None:
            return rest.union({end})
        return rest

    return NFA(alphabet=nfa.alphabet,
               transition_func=tsx,
               start_state=start,
               accepted_states=lambda x: x is end)


class GNFA:
    def __init__(self, states, alphabet, transitions, start_state, end_state):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.end_state = end_state

    get_outgoing = NFA.get_outgoing
    get_incoming = NFA.get_incoming

    def as_graph(self):
        return self.states, dict(
            (x, (y,)) for x, y in self.transitions.items())

    def accepted_states(self, st):
        return st == self.end_state

    def step(gnfa, node=None):
        if len(gnfa.states) == 2:
            raise ValueError()
        states = set(gnfa.states)
        # Pick a state that is not start/end
        if node is None:
            for elem in sorted(states):
                if elem != gnfa.start_state and elem != gnfa.end_state:
                    node = elem
                    break
        else:
            if node == gnfa.start_state:
                raise ValueError(
                    f"Node to remove {node} cannot be the start state.")
            if node == gnfa.end_state:
                raise ValueError(
                    f"Node to remove {node} cannot be the end state.")

        states.remove(node)
        tsx = {}
        si = set(states)
        si.remove(gnfa.end_state)
        sj = set(states)
        sj.remove(gnfa.start_state)
        for qi in si:
            for qj in sj:
                r1 = gnfa.transitions.get((qi, node), Nil)
                r2 = gnfa.transitions.get((node, node), Nil)
                r3 = gnfa.transitions.get((node, qj), Nil)
                r4 = gnfa.transitions.get((qi, qj), Nil)
                result = union(concat(r1, concat(star(r2), r3)), r4)
                if result is not Nil:
                    tsx[(qi, qj)] = result
        gnfa = GNFA(states, gnfa.alphabet, tsx, gnfa.start_state,
                    gnfa.end_state)
        return node, gnfa

    def reduce(gnfa):
        while len(gnfa.states) > 2:
            state, gnfa = gnfa.step()
            yield state, gnfa

    def to_regex(gnfa):
        m = list(g for (_, g) in gnfa.reduce())
        return m[-1].transitions.get((gnfa.start_state, gnfa.end_state), Empty)

    @classmethod
    def from_nfa(cls, nfa):
        nfa = wrap(nfa)
        start = nfa.start_state
        end, = nfa.end_states
        _, edges = nfa.as_graph()
        tsx = {}
        for (q1, q2), chars in edges.items():
            chars = list(Char(a) if a is not None else Empty for a in chars)
            tsx[(q1, q2)] = Union.from_list(chars)

        return cls(
            states=list(nfa.states),
            alphabet=nfa.alphabet,
            transitions=tsx,
            start_state=start,
            end_state=end,
        )


def regex_to_nfa(r, alphabet):
    if not isinstance(r, Regex):
        raise ValueError(r, type(r))
    if r is Nil:
        return NFA.make_nil(alphabet)
    elif r is Empty:
        return NFA.make_empty(alphabet)
    elif isinstance(r, Char):
        return NFA.make_char(alphabet, r.char)
    elif isinstance(r, Concat):
        return regex_to_nfa(r.left,
                            alphabet).concat(regex_to_nfa(r.right, alphabet))
    elif isinstance(r, Union):
        return regex_to_nfa(r.left,
                            alphabet).union(regex_to_nfa(r.right, alphabet))
    elif isinstance(r, Star):
        return regex_to_nfa(r.child, alphabet).star()


def nfa_to_regex(nfa: NFA) -> Regex:
    g = GNFA.from_nfa(nfa)
    return g.to_regex()


def tex_transition_name(e):
    text = repr(e)
    text = text.replace(repr(Empty), "\epsilon ")
    text = text.replace(repr(Nil), "\emptyset ")
    text = text.replace("*", "^\star ")
    text = text.replace("+", "+")
    return text


def save_tex(a, prefix, **kwargs):
    if "get_graph" not in kwargs:
        kwargs["get_graph"] = GNFA.as_graph
    if "transition_name" not in kwargs:
        kwargs["transition_name"] = tex_transition_name
    return render_dfa.save_tex(a, prefix, **kwargs)


def save_nfa_to_regex_dot(n, prefix, dry_run=False, **kwargs):
    def get_highlights(g, states):
        result = dict(kwargs)
        edges = set()
        for st in states:
            edges.update(frozenset((st, o) for o in g.get_outgoing(st)))
            edges.update(frozenset((i, st) for i in g.get_incoming(st)))
        result['highlight_nodes'] = states
        result['highlight_edges'] = edges
        return result

    # Saves the filenames recorded
    result = []

    # Write out wrapped
    w = wrap(n)
    nodes = w.start_state, tuple(w.end_states)[0]

    def on_tsx(args):
        return ", ".join(map(render_nfa.tex_transition_name, args))

    result.append(
        render_nfa.save_tex(
            w,
            prefix + "-wrapped-hl",
            dry_run=dry_run,
            **get_highlights(w, nodes),
            # transition_name=on_tsx,
        ))
    result.append(
        render_nfa.save_tex(
            w,
            prefix + "-wrapped",
            # transition_name=on_tsx,
            dry_run=dry_run,
            **kwargs))
    # Write out GNFA reduction
    g = GNFA.from_nfa(n)
    # Write out reduction steps
    steps = list(g.reduce())
    st = steps[0][0]
    result.append(
        save_tex(g,
                 prefix,
                 dry_run=dry_run,
                 transition_name=tex_transition_name,
                 **kwargs))
    result.append(
        save_tex(g, prefix + "-hl", dry_run=dry_run, **get_highlights(g,
                                                                      [st])))
    states = list(st for (st, _) in steps)
    del states[0]
    states.append(None)
    gs = (g for (_, g) in steps)
    for (idx, (st, g)) in enumerate(zip(states, gs)):
        hl = get_highlights(g, [st]) if st is not None else kwargs
        save_tex(g, f"{prefix}-hl-{idx + 1}", dry_run=dry_run, **hl)
        save_tex(g, f"{prefix}-{idx + 1}", dry_run=dry_run, **kwargs)
    return result
