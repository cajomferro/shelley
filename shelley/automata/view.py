import graphviz
from typing import Dict


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
