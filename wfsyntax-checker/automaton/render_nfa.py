from graphviz import *
import os
from collections import namedtuple
from . import render_dfa
from automaton import NFA

Step = namedtuple("Step", ["source", "input", "target"])

def merge(dict1, dict2):
  for k, v in dict2.items():
    dict1[k] = v.union(dict1.get(k, set()))

def multi_transition_edges(nfa, states, char):
  edges = set()
  for src in states:
    for dst in nfa.transition_func(src, char):
      edges.add((src, char, dst))
  return edges

def epsilon_edges(nfa, states):
  all_edges = row = multi_transition_edges(nfa, states, None)
  next_states = states.union(nfa.multi_transition(states, None))
  while len(next_states) != len(states):
    yield row
    states = next_states
    row = set()
    for edge in multi_transition_edges(nfa, states, None):
      if edge not in all_edges:
        all_edges.add(edge)
        row.add(edge)

    next_states = states.union(states.union(nfa.multi_transition(states, None)))

def edges_to_map(edges):
  result = dict()
  for (src, char, dst) in edges:
    key = (src, char)
    if key in result:
      data = result[key]
    else:
      result[key] = data = set()
    data.add(dst)
  return result

def accepts(nfa, inputs):
  states = nfa.epsilon({nfa.start_state})
  frontier = []
  for lvl in epsilon_edges(nfa, {nfa.start_state}):
    frontier.append(lvl)

  for idx, i in enumerate(inputs, 1):
    if len(states) == 0:
      return frontier, None
    assert i in nfa.alphabet or i is None, f"{repr(i)} not in {repr(nfa.alphabet)}"
    frontier.append(multi_transition_edges(nfa, states, i))
    states = nfa.multi_transition(states, i)
    for lvl in epsilon_edges(nfa, states):
      frontier.append(lvl)
    states = nfa.epsilon(states)

  return frontier, set(st for st in states if nfa.accepted_states(st))


def reduction_tree(levels, final, inputs):
  result = []
  nodes = {}
  for (idx, lvl) in enumerate(levels):
    lvl = edges_to_map(lvl)
    edges = []
    next_nodes = dict(nodes)
    for (_, outs) in lvl.items():
      for st in outs:
        next_nodes[st] = nodes.get(st, 0) + 1

    for ((src_st, inp), outs) in sorted(lvl.items()):
      for dst_st in outs:
        edges.append(Step(
            source=(src_st, (nodes if inp is not None else next_nodes).get(src_st, 0)),
            input=inp,
            target=(dst_st, next_nodes.get(dst_st, 0))))
    nodes = next_nodes
    result.append(edges)

  final = list((st, nodes.get(st, 0)) for st in final)
  final.sort()
  return result, final

def tree_to_dot(edges, final):
  node_id = lambda x: "%s_%d" % x
  dot = Digraph()
  dot.attr(
    d2tdocpreamble=r'\usetikzlibrary{automata}',
    d2tfigpreamble = r'\tikzstyle{every state}=[thick,fill=gray!20]',
    rankdir="LR")
  dot.edge_attr["lblstyle"] = "auto"

  nodes = set()
  for lvl in edges:
    for edge in lvl:
      nodes.add(edge.source)
      nodes.add(edge.target)

  for n in sorted(nodes):
    style = ["state"]
    if n in final:
      style.append("accepting")
    lbl = render_dfa.tex_state_name(n[0])
    dot.node(node_id(n), label=lbl, style=",".join(style))

  for lvl in edges:
    for edge in sorted(lvl):
      lbl = edge.input
      if hasattr(lbl, "__iter__"):
        lbl = "".join(map(str, lbl))
      else:
        lbl = tex_transition_name(lbl)
      dot.edge(
        node_id(edge.source),
        node_id(edge.target),
        label=lbl,
        style="thick")
  return dot

def save_reduction_dot(a, prefix, word, dry_run=False):
  lvls, final = accepts(a, word)
  edges, final = reduction_tree(lvls, final, word)
  dot = tree_to_dot(edges, final)
  filename = prefix + ".dot"
  if dry_run:
    return filename
  else:
    return dot.save(filename, os.getcwd())

def save_dot(a, prefix, **kwargs):
  if "get_graph" not in kwargs:
    kwargs["get_graph"] = NFA.as_graph
  return render.save_dot(a, prefix, **kwargs)

def tex_transition_name(x):
  return "\epsilon" if x is None else str(x)

def save_tex(a, prefix, **kwargs):
  if "get_graph" not in kwargs:
    kwargs["get_graph"] = NFA.as_graph
  if "transition_name" not in kwargs:
    kwargs["transition_name"] = tex_transition_name
  return render_dfa.save_tex(a, prefix, **kwargs)
