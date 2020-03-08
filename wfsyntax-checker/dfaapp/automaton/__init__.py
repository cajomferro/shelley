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

def minimize(alphabet, state_count, accepted_states, transitions):
    # https://www.cs.cornell.edu/courses/cs2800/2013fa/Handouts/minimization.pdf
    # marked as soon as a reason is discovered why p and q are not equivalent
    # Note: the table is symmetric, so we only store smaller-larger pairs
    accepted_states = set(accepted_states)
    unmarked = set()
    edges = [
        (src, dst)
        for src in range(state_count)
            for dst in range(src + 1, state_count)
    ]
    # Step 2: Mark{p,q} if 'p in F' XOR 'q in F'
    for p_q in edges:
        src, dst = p_q
        marked = (src in accepted_states) ^ (dst in accepted_states)
        # Unmarked entries are the ones where p in F <-> q in F
        # Aka, Mark {p,q} == false
        if not marked:
            unmarked.add(p_q)

    # next_to_mark:
    # there exists an un-marked pair{p,q} such that
    # {tsx(p,a),tsx(q,a)} is marked for some a in alphabet
    def next_to_mark(edges):
        # if there exists an un-marked pair{p,q}
        for p_q in unmarked:
            # for some a in alphabet
            for char in alphabet:
                # {tsx(p,a),tsx(q,a)} is marked
                # new_src, new_dst = {tsx(p,a),tsx(q,a)}
                # We sort the tuple because of symmetry
                new_pq = tuple(sorted(
                    transitions[(p_q[0], char)],
                    transitions[(p_q[1], char)]
                ))
                # new_pq is marked
                if new_pq not in unmarked:
                    return p_q
        # No pair was found
        return None

    # Step 3. Repeat the following until no more changes occur: if there exists
    # a pair{p,q} in next_to_mark then mark{p,q}.
    running = True
    while running:
        running = False
        pair = next_to_mark(unmarked)
        if pair is not None:
            unmarked.remove(pair)
            running = True

    # Finally we are ready to create the new automaton
    # p = q iff {p,q} unmarked
    # Unmarked means equivalent, if there are no equivalence classes
    # Then, there is nothing to minimize
    if len(unmarked) == 0:
        return transitions
    # Now we know which states are different
    # We build an array, such that for each state we know its
    # equivalent ancestor (self-loop means no other is same)
    states = list(range(state_count))
    for pq in edges:
        pq_same = pq in unmarked
        if pq_same:
            (p, q) = pq
            small, big = lex_order(p, q)
            states[big] = small
    # Given a state, returns the unique ancestor of each state
    def get_state(st):
        # XXX: We can improve performance by caching this step, but we are
        # XXX: already tight in memory.

        # Jump through list to get ancestor
        while states[st] != st:
            st = states[st]
        return st

    new_transitions = {}
    for (src,char), dst in transitions.items():
        # For each transition, only store the canonical state
        src = get_state(src)
        dst = get_state(dst)
        new_transitions[(src,char)] = dst
    return new_transitions


class DFA:
    def __init__(self, alphabet, transition_func, start_state,
                 accepted_states):
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

        return DFA(alphabet=frozenset(dfa1.alphabet).union(dfa2.alphabet),
                   transition_func=transition,
                   start_state=(dfa1.start_state, dfa2.start_state),
                   accepted_states=is_final)

    def intersection(dfa1, dfa2):
        def transition(q, a):
            q1, q2 = q
            return (dfa1.transition_func(q1, a), dfa2.transition_func(q2, a))

        def is_final(q):
            q1, q2 = q
            return dfa1.accepted_states(q1) and dfa2.accepted_states(q2)

        return DFA(alphabet=frozenset(dfa1.alphabet).union(dfa2.alphabet),
                   transition_func=transition,
                   start_state=(dfa1.start_state, dfa2.start_state),
                   accepted_states=is_final)

    def complement(dfa):
        is_final = dfa.accepted_states
        return DFA(
            alphabet = dfa.alphabet,
            transition_func = dfa.transition_func,
            start_state = dfa.start_state,
            accepted_states = lambda x: not is_final(x)
        )

    def convert_to_nfa(dfa):
        return NFA(alphabet=dfa.alphabet,
                   transition_func=lambda q, a: {
                       dfa.transition_func(q, a),
                   } if a is not None else {},
                   start_state=dfa.start_state,
                   accepted_states=dfa.accepted_states)

    def subtract(dfa1, dfa2):
        return dfa1.intersection(dfa2.complement())

    def contains(dfa1, dfa2):
        return dfa2.subtract(dfa1).is_empty()

    def transitions(dfa):
        visited_nodes = set()
        to_visit = [dfa.start_state]
        while len(to_visit) > 0:
            src = to_visit.pop()
            if src in visited_nodes:
                continue
            # New node
            visited_nodes.add(src)
            outgoing = []
            for char in dfa.alphabet:
                dst = dfa.transition_func(src, char)
                outgoing.append((char, dst))
                to_visit.append(dst)
            yield (src, outgoing)

    def flatten(self, minimize=False) -> "DFA":
        """
        Flatten returns a new DFA that caches all of its transitions,
        essentially improving time but reducing space.
        """
        state_to_id = {}
        def get_state_id(st):
            st_id = state_to_id.get(st, None)
            if st_id is None:
                st_id = len(state_to_id)
                state_to_id[st] = st_id
            return st_id

        transitions = {}
        accepted_states = []
        for (src, out) in self.transitions():
            src_id = get_state_id(src)
            if self.accepted_states(src):
                accepted_states.append(src_id)
            for (char, dst) in out:
                dst_id = get_state_id(dst)
                transitions[(src_id, char)] = dst_id
        if minimize:
            transitions = minimize(self.alphabet,
                len(state_to_id),
                accepted_states,
                transitions
            )
        return DFA(
            alphabet=self.alphabet,
            transition_func=lambda src, char: transitions[(src, char)],
            start_state=state_to_id[self.start_state],
            accepted_states=accepted_states.__contains__
        )


    @property
    def states(self):
        for src, _ in self.transitions():
            yield src

    def is_empty(self):
        for node, _ in self.transitions():
            if self.accepted_states(node):
                return False
        return True

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
        visited_nodes = set()
        edges = {}
        for src, outs in dfa.transitions():
            visited_nodes.add(src)
            for (char, dst) in outs:
                chars = edges.get((src, dst), set())
                chars.add(char)
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
        return cls(alphabet=alphabet,
                   transition_func=lambda q, a: 1,
                   start_state=0,
                   accepted_states=lambda x: x == 0)

    @classmethod
    def make_char(cls, alphabet, char):
        assert char in alphabet
        return cls(alphabet=alphabet,
                   transition_func=lambda q, a: 1
                   if q == 0 and a == char else 2,
                   start_state=0,
                   accepted_states=lambda x: x == 1)

    @classmethod
    def make_nil(cls, alphabet):
        Q1 = 0

        def transition(q, a):
            return q

        return cls(alphabet, transition, Q1, lambda x: False)


class NFA:
    def __init__(self, alphabet, transition_func, start_state,
                 accepted_states):
        self.alphabet = alphabet
        self.transition_func = transition_func
        self.start_state = start_state
        self.accepted_states = wrap_accepted_states(accepted_states)

    def multi_transition(self, states, input):
        new_states = set()
        for st in states:
            #assert st in self.states, f"{st} in {self.states}"
            new_states.update(self.transition_func(st, input))
        return frozenset(new_states)

    def epsilon(self, states):
        #for idx, st in enumerate(states, 1):
        #    if st not in self.states:
        #        raise ValueError(
        #            f"Error at state #{idx}={repr(st)} not in states={self.states}"
        #        )
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

    def union(nfa1, nfa2):
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
            start_state=(nfa1.start_state, nfa2.start_state),
            accepted_states=is_final,
            transition_func=transition,
        )

    def concat(nfa1, nfa2):
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

        return DFA(alphabet=nfa.alphabet,
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

    def get_states(nfa):
        visited_nodes = set()
        to_visit = [nfa.start_state]
        alpha = set(nfa.alphabet)
        alpha.add(None)
        while len(to_visit) > 0:
            src = to_visit.pop()
            if src in visited_nodes:
                continue
            # New node
            visited_nodes.add(src)
            outgoing = []
            for char in alpha:
                for dst in nfa.transition_func(src, char):
                    outgoing.append((char, dst))
                    to_visit.append(dst)
            yield (src, outgoing)

    @property
    def states(self):
        for src,_ in self.get_states():
            yield src

    def as_graph(nfa):
        visited_nodes = set()
        edges = {}
        for (src, out) in nfa.get_states():
            visited_nodes.add(src)
            for (char, dst) in out:
                chars = edges.get((src, dst), set())
                chars.add(char)
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
        return cls(alphabet=alphabet,
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
        Q1, Q2 = range(2)

        def transition(q, a):
            return {Q2} if a == char and q == Q1 else {}

        return cls(alphabet, transition, Q1, lambda x: x == Q2)

    @classmethod
    def make_nil(cls, alphabet):
        Q1 = 0

        def transition(q, a):
            return frozenset()

        return cls([Q1], alphabet, transition, Q1, lambda x: False)
