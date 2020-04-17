import graphviz
from typing import Dict


def automaton2dot(automaton: Dict) -> graphviz.Digraph:
    """
    :param automaton: YAML checked device as dict
    :return:
    """
    dot = graphviz.Digraph()
    nodes = set(k for edge in automaton["edges"] for k in (edge["src"], edge["dst"]))
    nodes.add(automaton["start_state"])
    nodes.union(automaton["accepted_states"])
    accepted = set(automaton["accepted_states"])
    for node in sorted(nodes):
        kwargs = {"shape": "circle"}
        if node == automaton["start_state"] and node in accepted:
            kwargs["shape"] = "doubleoctagon"
        elif node == automaton["start_state"]:
            kwargs["shape"] = "octagon"
        elif node in accepted:
            kwargs["shape"] = "doublecircle"
        dot.node(str(node), **kwargs)
    # Group by edges:
    edges = {}
    for edge in automaton["edges"]:
        pair = str(edge["src"]), str(edge["dst"])
        outs = edges.get(pair, None)
        if outs is None:
            edges[pair] = outs = []
        outs.append(edge["char"])
    # Create an edge per edge
    for ((src, dst), chars) in sorted(edges.items()):
        chars = sorted(map(str, chars))
        dot.edge(src, dst, label=", ".join(chars))

    return dot
