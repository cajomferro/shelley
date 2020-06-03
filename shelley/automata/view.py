import graphviz
from typing import Dict, Any, Callable, Optional, Union
from graphviz import Digraph
from karakuri import regular


def render_state(name: Any) -> Any:
    if isinstance(name, int):
        return f"q_{{ {name} }}"
    return str(name)


def render_edge(name: Any) -> str:
    if name is None:
        return "\\epsilon"
    return f"{{\\tt {name} }}"


def fsm2tex(
    fsm: regular.NFA[Any, str],
    state_name: Callable[[Any], str] = render_state,
    transition_name: Callable[[Any], str] = render_edge,
    initial_orientation: Optional[str] = None,
    fig_only: bool = False,
    char_sep: str = ",",
) -> graphviz.Digraph:
    dot = Digraph()
    dot.attr(
        d2tfigpreamble=r"\tikzstyle{every state}=[thick,fill=gray!20]", rankdir="LR"
    )
    dot.node_attr["style"] = "state"
    dot.edge_attr["lblstyle"] = "auto,align=left"
    dot.edge_attr["style"] = "thick"
    if fig_only:
        dot.attr(d2toptions="--figonly")
    else:
        dot.attr(d2tdocpreamble=r"\usetikzlibrary{automata}")

    initial = ["initial"]
    if initial_orientation is not None:
        initial.append(initial_orientation)

    nodes, edges = fsm.as_graph()

    for state in sorted(nodes):
        kwargs = dict()
        style = ["state"]
        if fsm.accepted_states(state):
            style.append("accepting")
        if state == fsm.start_state:
            style.append(" ".join(initial))
        kwargs["style"] = ",".join(style)
        kwargs["label"] = state_name(state)
        dot.node(str(state), **kwargs)

    for ((src, dst), chars) in sorted(edges.items()):
        str_chars = sorted(map(transition_name, chars))
        dot.edge(str(src), str(dst), label=char_sep.join(str_chars))

    return dot


def transition_name_txt(name: Any) -> str:
    return str(name) if name is not None else "ε"


def fsm2dot(
    fsm: regular.NFA[Any, str],
    transition_name: Callable[[Any], str] = transition_name_txt,
    state_name=str,
    char_sep=",",
) -> graphviz.Digraph:

    """
    :param automaton: YAML checked device as dict
    :return:
    """
    dot = graphviz.Digraph()
    dot.graph_attr["rankdir"] = "LR"
    dot.node("", shape="point")  # start point
    nodes, edges = fsm.as_graph()

    for node in sorted(nodes):
        kwargs = {"shape": "circle"}
        if node == fsm.start_state:
            start_node_lbl: str = str(node)
        if fsm.accepted_states(node):
            kwargs["shape"] = "doublecircle"
        dot.node(str(node), **kwargs)

    dot.edge("", str(fsm.start_state), label="")  # arrow for start state
    for ((src, dst), chars) in sorted(edges.items()):
        str_chars = sorted(map(transition_name, chars))
        dot.edge(state_name(src), state_name(dst), label=char_sep.join(str_chars))
    return dot
