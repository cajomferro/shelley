from graphviz import Digraph
import os


def step(dfa, inputs):
    if dfa.accepts(inputs):
        st = dfa.start_state
        for i in inputs:
            st = dfa.transition_func(st, i)
            yield st


def build(m,
          get_graph=None,
          highlight_nodes=(),
          highlight_edges=(),
          extra_edge_style=lambda src, dst, kwargs: (),
          state_name=str,
          transition_name=str,
          initial_orientation=None,
          edge_stack=False,
          fig_only=False):
    dot = Digraph()
    dot.attr(d2tdocpreamble=r'\usetikzlibrary{automata}',
             d2tfigpreamble=r'\tikzstyle{every state}=[thick,fill=gray!20]',
             rankdir="LR")
    dot.node_attr["style"] = "state"
    dot.edge_attr["lblstyle"] = "auto,align=left"
    dot.edge_attr["style"] = "thick"
    if fig_only:
        dot.attr(d2toptions='--figonly')

    initial = ["initial"]
    if initial_orientation is not None:
        initial.append(initial_orientation)

    nodes, edges = get_graph(m) if get_graph is not None else m.as_graph()

    for state in sorted(nodes):
        kwargs = dict()
        style = ['state']
        if m.accepted_states(state):
            style.append('accepting')
        if state == m.start_state:
            style.append(" ".join(initial))
        if state in highlight_nodes:
            style.append("fill=yellow!20")
        kwargs["style"] = ",".join(style)
        dot.node(state_name(state), **kwargs)
    char_sep = " $\\\\\\\\$ " if edge_stack else ","
    for ((src, dst), chars) in sorted(edges.items()):
        if (src, dst) in highlight_edges:
            kwargs = dict(style="color=brown,line width=2pt")
        else:
            kwargs = dict()
        extra_edge_style(src, dst, kwargs)
        chars = sorted(map(transition_name, chars))
        dot.edge(state_name(src),
                 state_name(dst),
                 label=char_sep.join(chars),
                 **kwargs)

    return dot


def save_dot(a, prefix, **kwargs):
    filename = prefix + ".dot"
    dry_run = kwargs.get("dry_run", False)
    if "dry_run" in kwargs:
        del kwargs["dry_run"]

    b = build(a, **kwargs)
    if dry_run:
        return filename
    else:
        return b.save(filename, directory=os.path.realpath(
            os.path.join(os.getcwd(), 'dot_output')))  # TODO: this should a parameter


def tex_state_name(q):
    if isinstance(q, frozenset) or isinstance(q, set):
        return "\{" + ", ".join(map(tex_state_name, q)) + "\}"
    if isinstance(q, str):
        return q
    if isinstance(q, int):
        return f"q_{q + 1}"
    if q == ():
        return "init"
    if isinstance(q, tuple):
        indices = []
        while isinstance(q, tuple):
            idx, q = q
            indices.append(idx + 1)
        indices.append(q + 1)
        indices.reverse()
        indices = ",".join(map(str, indices))
        indices = "{" + indices + "}"
        return f"q_{indices}"
    return repr(q)


def save_tex(a, prefix, **kwargs):
    if "state_name" not in kwargs:
        kwargs["state_name"] = tex_state_name
    return save_dot(a, prefix, **kwargs)


def save_reduction_dot(a, prefix, inputs, **kwargs):
    result = []
    dry_run = kwargs.get("dry_run", False)
    if "dry_run" in kwargs:
        del kwargs["dry_run"]
    if dry_run:

        def do_save(counter):
            result.append("%s%d.dot" % (prefix, counter))
            return counter + 1
    else:

        def do_save(counter):
            result.append(
                d.save("%s%d.dot" % (prefix, counter), directory=os.getcwd()))
            return counter + 1

    d = build(a, highlight_nodes=[a.start_state], **kwargs)
    counter = 1
    counter = do_save(counter)
    prev = a.start_state
    for i, s in zip(inputs, step(a, inputs)):
        d = build(a,
                  highlight_edges=[(prev, s)],
                  highlight_nodes=[s],
                  **kwargs)
        counter = do_save(counter)
        prev = s
    return result


if __name__ == '__main__':
    import doctest

    doctest.testmod()
