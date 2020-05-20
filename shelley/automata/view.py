import graphviz
from typing import Dict
from graphviz import Digraph
from karakuri import regular

def render_state(name):
    if isinstance(name, int):
        return f"q_{{ {name} }}"

def render_edge(name):
    return f'{{\\tt {name} }}'

def dfa2tex(data,
          get_graph=None,
          state_name=render_state,
          transition_name=render_edge,
          initial_orientation=None,
          fig_only=False,
          char_sep=","):
    m = regular.NFA.from_dict(data)
    dot = Digraph()
    dot.attr(d2tfigpreamble=r'\tikzstyle{every state}=[thick,fill=gray!20]',
             rankdir="LR")
    dot.node_attr["style"] = "state"
    dot.edge_attr["lblstyle"] = "auto,align=left"
    dot.edge_attr["style"] = "thick"
    if fig_only:
        dot.attr(d2toptions='--figonly')
    else:
        dot.attr(d2tdocpreamble=r'\usetikzlibrary{automata}')


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
        kwargs["style"] = ",".join(style)
        dot.node(state_name(state), **kwargs)

    for ((src, dst), chars) in sorted(edges.items()):
        chars = sorted(map(transition_name, chars))
        dot.edge(state_name(src),
                 state_name(dst),
                 label=char_sep.join(chars),
                 **kwargs)

    return dot


def automaton2dot(automaton: Dict) -> graphviz.Digraph:
    """
    :param automaton: YAML checked device as dict
    :return:
    """
    dot = graphviz.Digraph()
    dot.graph_attr["rankdir"] = "LR"
    nodes = set(k for edge in automaton["edges"] for k in (edge["src"], edge["dst"]))
    nodes.add(automaton["start_state"])
    nodes.union(automaton["accepted_states"])
    accepted = set(automaton["accepted_states"])
    dot.node("", shape="point")  # start point
    for node in sorted(nodes):
        kwargs = {"shape": "circle"}
        if node == automaton["start_state"]:
            start_node_lbl: str = str(node)
        # if node == automaton["start_state"] and node in accepted:
        #     kwargs["shape"] = "doubleoctagon"
        # elif node == automaton["start_state"]:
        #     kwargs["shape"] = "octagon"
        if node in accepted:
            kwargs["shape"] = "doublecircle"
        dot.node(str(node), **kwargs)
    # Group by edges:
    edges: Dict = {}
    for edge in automaton["edges"]:
        pair = str(edge["src"]), str(edge["dst"])
        outs = edges.get(pair, None)
        if outs is None:
            edges[pair] = outs = []
        outs.append(edge["char"])
    # Create an edge per edge
    dot.edge("", start_node_lbl, label="")  # arrow for start state
    for ((src, dst), chars) in sorted(edges.items()):
        chars = sorted(map(str, chars))
        dot.edge(src, dst, label=", ".join(chars))

    return dot
