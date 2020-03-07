from itertools import combinations, chain, product


def wrap_accepted_states(accepted_states):
    if callable(accepted_states):
        return accepted_states
    return lambda x: x in accepted_states


def powerset(iterable):
    s = list(iterable)
    result = []
    for r in range(len(s) + 1):
        for cmb in combinations(s, r):
            result.append(frozenset(cmb))
    return result


def tag(st, iterable):
    return map(lambda x: (st, x), iterable)


class DFA:
    def __init__(self, states, alphabet, transition_func, start_state,
                 accepted_states):
        assert start_state in states, "%r in %r" % (start_state, states)
        self.states = states
        self.alphabet = alphabet
        self.transition_func = transition_func
        self.start_state = start_state
        self.accepted_states = wrap_accepted_states(accepted_states)

    def accepts(self, inputs):
        st = self.start_state
        for i in inputs:
            assert i in self.alphabet, f"{i} not in {self.alphabet}"
            st = self.transition_func(st, i)
            assert st in self.states, f"{st} not in {self.states}"
        return self.accepted_states(st)

    def union(dfa1, dfa2):
        def transition(q, a):
            q1, q2 = q
            return (dfa1.transition_func(q1, a), dfa2.transition_func(q2, a))

        def is_final(q):
            q1, q2 = q
            return dfa1.accepted_states(q1) or dfa2.accepted_states(q2)

        return DFA(states=frozenset(product(dfa1.states, dfa2.states)),
                   alphabet=frozenset(dfa1.alphabet).union(dfa2.alphabet),
                   transition_func=transition,
                   start_state=(dfa1.start_state, dfa2.start_state),
                   accepted_states=is_final)

    def concat(dfa1, dfa2):
        return dfa1.convert_to_nfa().concat(dfa2.convert_to_nfa())

    def convert_to_nfa(dfa):
        return NFA(states=dfa.states,
                   alphabet=dfa.alphabet,
                   transition_func=lambda q, a: {
                       dfa.transition_func(q, a),
                   } if a is not None else {},
                   start_state=dfa.start_state,
                   accepted_states=dfa.accepted_states)

    def get_table(self):
        row = [None]
        for k in self.alphabet:
            row.append(k)
        yield row
        for q in self.states:
            row = [q]
            for k in self.alphabet:
                row.append(self.transition_func(q, k))
            yield row

    def get_minimized_graph(dfa):
        visited_edges = set()
        visited_nodes = set()
        to_visit = [dfa.start_state]
        while len(to_visit) > 0:
            src = to_visit.pop()
            if src in visited_nodes:
                continue
            visited_nodes.add(src)
            for char in dfa.alphabet:
                dst = dfa.transition_func(src, char)
                edge = (src, char, dst)
                visited_edges.add(edge)
                to_visit.append(dst)
        edges = {}
        # Merge edges
        for (src, char, dst) in visited_edges:
            chars = edges.get((src, dst), [])
            chars.append(char)
            edges[(src, dst)] = chars
        return visited_nodes, edges

    def get_full_graph(dfa):
        edges = {}
        for state in dfa.states:
            for inp in dfa.alphabet:
                next_state = dfa.transition_func(state, inp)
                if next_state is not None:
                    if state not in edges:
                        out = {}
                        edges[state] = out
                    else:
                        out = edges[state]
                    if next_state in out:
                        out[next_state].append(inp)
                    else:
                        out[next_state] = [inp]

        nodes = dfa.states
        result = dict()
        for (src, outs) in edges.items():
            for (dst, chars) in outs.items():
                result[(src, dst)] = chars
        return nodes, result

    as_graph = get_minimized_graph

    @property
    def end_states(self):
        return filter(self.accepted_states, self.states)

    def __repr__(self):
        data = dict(start_state=self.start_state,
                    accepted_states=list(self.end_states),
                    transitions=dict(self.as_graph()[1]))
        return f'DFA({data})'

    @staticmethod
    def transition_table(table, sink=None):
        if sink is None:

            def func(old_st, i):
                return table[(old_st, i)]
        else:

            def func(old_st, i):
                return table.get((old_st, i), sink)

        return func

    @classmethod
    def make_empty(cls, alphabet):
        return cls(states=[0, 1],
                   alphabet=alphabet,
                   transition_func=lambda q, a: 1,
                   start_state=0,
                   accepted_states=lambda x: x == 0)

    @classmethod
    def make_char(cls, alphabet, char):
        assert char in alphabet
        return cls(states=[0, 1, 2],
                   alphabet=alphabet,
                   transition_func=lambda q, a: 1
                   if q == 0 and a == char else 2,
                   start_state=0,
                   accepted_states=lambda x: x == 1)

    @classmethod
    def make_nil(cls, alphabet):
        Q1 = 0

        def transition(q, a):
            return q

        return cls([Q1], alphabet, transition, Q1, lambda x: False)


class NFA:
    def __init__(self, states, alphabet, transition_func, start_state,
                 accepted_states):
        assert start_state in states, f"start_state={start_state} not in states={states}"
        self.states = states
        self.alphabet = alphabet
        self.transition_func = transition_func
        self.start_state = start_state
        self.accepted_states = wrap_accepted_states(accepted_states)

    def multi_transition(self, states, input):
        new_states = set()
        for st in states:
            assert st in self.states, f"{st} in {self.states}"
            new_states.update(self.transition_func(st, input))
        return frozenset(new_states)

    def epsilon(self, states):
        for idx, st in enumerate(states, 1):
            if st not in self.states:
                raise ValueError(
                    f"Error at state #{idx}={repr(st)} not in states={self.states}"
                )
        states = set(states)
        while True:
            count = len(states)
            states.update(self.multi_transition(states, None))
            if count == len(states):
                return frozenset(states)

    def accepts(self, inputs):
        # Perform epsilon transitions of the state
        states = self.epsilon({self.start_state})
        for idx, i in enumerate(inputs, 1):
            if len(states) == 0:
                # Not accepted
                return False
            # Get the transitions and then perform epsilon transitions
            states = self.epsilon(self.multi_transition(states, i))
        return len(set(filter(self.accepted_states, states))) > 0

    def complement(nfa):
        return NFA(
            states = frozenset(nfa.states),
            alphabet = frozenset(nfa.alphabet),
            transition_func = nfa.transition_func,
            start_state = nfa.start_state,
            accepted_states = lambda x: not nfa.accepted_states(x)
        )

    def intersection(nfa1, nfa2):
        return nfa1.complement().union(nfa2.complement()).complement()

    def subtract(nfa1, nfa2):
        # We implement the intersection in terms of the union.
        # Thus, rather than A = /\ ~ B, I just write the simplified form:
        # A /\ ~ B = ~ (~ A \/ ~ ~ B ) = ~ (A \/ B)
        return nfa1.complement().union(nfa2).complement()

    def union(nfa1, nfa2):
        states = set(tag(0, nfa1.states))
        states.update(tag(1, nfa2.states))
        states.add((2, 0))
        tsx = (nfa1.transition_func, nfa2.transition_func)
        fin = (nfa1.accepted_states, nfa2.accepted_states)

        def transition(st, a):
            idx, st = st
            if idx == 2:
                return frozenset({(0, nfa1.start_state), (1, nfa2.start_state)
                                  }) if a is None else frozenset()

            return frozenset(tag(idx, tsx[idx](st, a)))

        def is_final(st):
            idx, st = st
            if idx == 2:
                return False
            return fin[idx](st)

        return NFA(
            states=frozenset(states),
            alphabet=frozenset(nfa1.alphabet).union(nfa2.alphabet),
            transition_func=transition,
            accepted_states=is_final,
            start_state=(2, 0),
        )

    def shuffle(nfa1, nfa2):
        def transition(st, a):
            (st1, st2) = st
            result = set()
            if a is None:
                result.update(
                    (st1, st2) for st1 in nfa1.transition_func(st1, a))
                result.update(
                    (st1, st2) for st2 in nfa2.transition_func(st2, a))
                return result

            if a in nfa1.alphabet:
                result.update(
                    (st1, st2) for st1 in nfa1.transition_func(st1, a))

            if a in nfa2.alphabet:
                result.update(
                    (st1, st2) for st2 in nfa2.transition_func(st2, a))

            return frozenset(result)

        def is_final(st):
            st1, st2 = st
            return nfa1.accepted_states(st1) and nfa2.accepted_states(st2)

        return NFA(
            alphabet=frozenset(nfa1.alphabet).union(nfa2.alphabet),
            states=tuple(product(nfa1.states, nfa2.states)),
            start_state=(nfa1.start_state, nfa2.start_state),
            accepted_states=is_final,
            transition_func=transition,
        )

    def concat(nfa1, nfa2):
        states = set(tag(0, nfa1.states))
        states.update(tag(1, nfa2.states))
        tsx = (nfa1.transition_func, nfa2.transition_func)
        fin = (nfa1.accepted_states, nfa2.accepted_states)

        def transition(st, a):
            idx, st = st
            # Add an extra edge
            if idx == 0 and nfa1.accepted_states(st) and a is None:
                return frozenset({(1, nfa2.start_state)}).union(
                    frozenset(
                        map(lambda x: (0, x), nfa1.transition_func(st, a))))
            return frozenset(tag(idx, tsx[idx](st, a)))

        def is_final(st):
            idx, st = st
            return idx == 1 and nfa2.accepted_states(st)

        return NFA(
            states=frozenset(states),
            alphabet=frozenset(nfa1.alphabet).union(nfa2.alphabet),
            transition_func=transition,
            accepted_states=is_final,
            start_state=(0, nfa1.start_state),
        )

    def star(nfa):
        def transition(st, a):
            idx, st = st
            if idx == 0:
                return frozenset({(1, nfa.start_state)
                                  }) if a is None else frozenset()
            result = set(tag(1, nfa.transition_func(st, a)))
            if a is None and nfa.accepted_states(st):
                result.add((0, 0))  # Return back to the initial state
            return frozenset(result)

        def is_final(st):
            idx, st = st
            return idx == 0 or nfa.accepted_states(st)

        return NFA(
            states=frozenset(chain(tag(1, nfa.states), [(0, 0)])),
            alphabet=nfa.alphabet,
            transition_func=transition,
            accepted_states=[(0, 0)],
            start_state=(0, 0),
        )

    def convert_to_dfa(nfa):
        def transition(q, c):
            if not isinstance(q, frozenset):
                raise ValueError(q)
            return nfa.epsilon(nfa.multi_transition(q, c))

        def accept_state(qs):
            for q in qs:
                if nfa.accepted_states(q):
                    return True
            return False

        return DFA(states=powerset(nfa.states),
                   alphabet=nfa.alphabet,
                   transition_func=transition,
                   start_state=nfa.epsilon({nfa.start_state}),
                   accepted_states=accept_state)

    @property
    def transitions(self):
        return self.as_graph()[1]

    def get_outgoing(self, node):
        return (dst for (src, dst) in self.transitions if src == node)

    def get_incoming(self, node):
        return (src for (src, dst) in self.transitions if dst == node)

    def as_graph(nfa):
        visited_edges = set()
        visited_nodes = set()
        to_visit = [nfa.start_state]
        alpha = set(nfa.alphabet)
        alpha.add(None)
        while len(to_visit) > 0:
            src = to_visit.pop()
            if src in visited_nodes:
                continue
            visited_nodes.add(src)
            for char in alpha:
                for dst in nfa.transition_func(src, char):
                    edge = (src, char, dst)
                    visited_edges.add(edge)
                    to_visit.append(dst)
        edges = {}
        # Merge edges
        for (src, char, dst) in visited_edges:
            chars = edges.get((src, dst), [])
            chars.append(char)
            edges[(src, dst)] = chars
        return visited_nodes, edges

    @property
    def end_states(self):
        return filter(self.accepted_states, self.states)

    def __repr__(self):
        data = dict(start_state=self.start_state,
                    accepted_states=list(self.end_states),
                    transitions=dict(self.as_graph()[1]))
        return f'NFA({data})'

    @classmethod
    def make_empty(cls, alphabet):
        Q1 = 0
        return cls(states=[Q1],
                   alphabet=alphabet,
                   transition_func=lambda q, a: frozenset(),
                   start_state=Q1,
                   accepted_states=lambda x: x == Q1)

    @staticmethod
    def transition_edges(edges):
        tsx = dict()
        for (src, chars, dst) in edges:
            for char in chars:
                elems = tsx.get((src, char), frozenset())
                elems = elems.union({dst})
                tsx[(src, char)] = elems
        return DFA.transition_table(tsx, frozenset())

    @staticmethod
    def transition_table(table):
        def func(old_st, i):
            return table.get((old_st, i), set())

        return func

    @classmethod
    def from_transition_edges(cls, edges, **kwargs):
        if "states" not in kwargs:
            kwargs["states"] = set(k for (x, _, y) in edges for k in (x, y))
        if "alphabet" not in kwargs:
            kwargs["alphabet"] = set(k for (_, elems, _) in edges
                                     for k in elems)
        return cls(transition_func=cls.transition_edges(edges), **kwargs)

    @classmethod
    def make_char(cls, alphabet, char):
        if char not in alphabet:
            raise ValueError(f"{repr(char)} not in {repr(alphabet)}")
        states = Q1, Q2 = range(2)

        def transition(q, a):
            return {Q2} if a == char and q == Q1 else {}

        return cls(states, alphabet, transition, Q1, lambda x: x == Q2)

    @classmethod
    def make_nil(cls, alphabet):
        Q1 = 0

        def transition(q, a):
            return frozenset()

        return cls([Q1], alphabet, transition, Q1, lambda x: False)
