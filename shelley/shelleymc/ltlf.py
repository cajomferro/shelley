from typing import List
from shelley.parsers.shelley_lark_parser import parse
from pathlib import Path
from dataclasses import dataclass
from shelley.parsers.ltlf_lark_parser import (
    And,
    Equal,
    Action,
    Not,
    Always,
    Next,
    Implies,
    Or,
    Until,
    Bool,
    Eventually,
    Formula,
)
from shelley.parsers.ltlf_lark_parser import parser as ltlf_parser
import io

# LTLSPEC (action=level1) -> (action=standby1 | action=level1);
def smv_dump(state_diagram, var_action="_action", var_eos="_eos", var_state="_state"):
    dump = io.StringIO()

    to_act = lambda x: x if x is None else x.replace(".", "_")
    INDENT = "    "

    def render_values(elem):
        if isinstance(elem, str):
            return elem
        if len(elem) == 0:
            raise ValueError()
        return "{" + ", ".join(map(str, elem)) + "}"

    def decl_var(name, values):
        print(f"{INDENT}{name}: {render_values(values)};", file=dump)

    def add_edge(src, char, dst):
        char = to_act(char)
        act = f" & {var_action}={char}" if char is not None else ""
        print(f"{var_state}={src}{act}: {dst};", file=dump)

    def init_var(name, values):
        print(f"{INDENT}init({name}) := {render_values(values)};", file=dump)

    def next_var_case(variable, elems):
        print(f"{INDENT}next({variable}) := case", file=dump)
        for (cond, res) in elems:
            res = render_values(res)
            print(f"{INDENT}{INDENT}{cond} : {res};", file=dump)
        print(f"{INDENT}esac;", file=dump)

    acts = list(
        set(
            to_act(edge["char"])
            for edge in state_diagram["edges"]
            if edge["char"] is not None
        )
    )
    acts.sort()
    print("MODULE main", file=dump)
    print("VAR", file=dump)
    decl_var(f"{var_eos}", "boolean")
    decl_var(f"{var_action}", acts)

    states = list(
        set(x["src"] for x in state_diagram["edges"]).union(
            set(x["src"] for x in state_diagram["edges"])
        )
    )
    states.sort()
    decl_var(f"{var_state}", states)
    print("ASSIGN", file=dump)

    # State
    init_var(f"{var_state}", [state_diagram["start_state"]])
    print(f"{INDENT}next({var_state}) := case", file=dump)
    print(
        f"{INDENT}{INDENT}{var_eos}: {var_state}; -- finished, no change in state",
        file=dump,
    )
    for edge in state_diagram["edges"]:
        print(f"{INDENT}{INDENT}", end="", file=dump)
        src, char, dst = edge["src"], edge["char"], edge["dst"]
        add_edge(src, char, dst)
    print(f"{INDENT}esac;", file=dump)
    # Action
    if len(acts) > 1:
        init_var(f"{var_action}", acts)
        next_var_case(var_action, [(var_eos, var_action), ("TRUE", acts)])

    # EOS
    init_var(
        var_eos,
        ["TRUE", "FALSE"]
        if state_diagram["start_state"] in state_diagram["accepted_states"]
        else ["FALSE"],
    )
    lines = [
        (var_eos, "TRUE"),
    ]
    for edge in state_diagram["edges"]:
        src, char, dst = edge["src"], edge["char"], edge["dst"]
        if dst in state_diagram["accepted_states"]:
            char = to_act(char)
            act = f" & {var_action}={char}" if char is not None else ""
            lines.append((f"{var_state}={src}{act}", ["TRUE", "FALSE"]))
    lines.append(("TRUE", "FALSE"))
    next_var_case(var_eos, lines)
    print(f"FAIRNESS {var_eos};", file=dump)

    print(f"LTLSPEC F ({var_eos}); -- sanity check", file=dump)
    print(
        f"LTLSPEC G ({var_eos} -> G({var_eos}) & X({var_eos})); -- sanity check",
        file=dump,
    )

    return dump


def ltlf2ltl(formula, name, eos_var, action_var):
    """
    Converts an LTLf formula in an LTL formula
    """

    def rec(formula):
        if isinstance(formula, Bool):
            return formula
        if isinstance(formula, Action):
            if name is not None:
                formula = Action(name=name + "_" + formula.name)
            return And(Equal(action_var, formula), Not(eos_var))
        elif isinstance(formula, Not):
            return Not(rec(formula.formula))
        elif isinstance(formula, Or):
            return Or(rec(formula.left), rec(formula.right))
        elif isinstance(formula, Equal):
            return Equal(rec(formula.left), rec(formula.right))
        elif isinstance(formula, And):
            return And(rec(formula.left), rec(formula.right))
        elif isinstance(formula, Implies):
            return Implies(rec(formula.left), rec(formula.right))
        elif isinstance(formula, Next):
            return Next(And(rec(formula.formula), Not(eos_var)))
        elif isinstance(formula, Eventually):
            return Eventually(And(rec(formula.formula), Not(eos_var)))
        elif isinstance(formula, Always):
            return Always(Or(rec(formula.formula), eos_var))
        elif isinstance(formula, Until):
            return Until(
                left=rec(formula.left), right=And(rec(formula.right), Not(eos_var))
            )
        raise TypeError(formula)

    return rec(formula)


def generate_formula(formulas, name, eos_var, action_var):
    for formula in formulas:
        tree = ltlf_parser.parse(formula)
        ltlf = ltlf_parser.LTLParser().transform(tree)
        print(
            "LTLSPEC",
            ltlf2ltl(ltlf, name=name, eos_var=eos_var, action_var=action_var,),
        )


@dataclass
class Op:
    targets: list
    is_final: bool

    @classmethod
    def make(cls, is_final=False):
        return cls([], is_final)

    def add(self, name):
        self.targets.append(name)


@dataclass
class LTLSpec:
    f: Formula

    def __str__(self):
        return f"LTLSPEC {self.f} ;"


def generate_spec(
    spec_path: Path, prefix: str, eos: Action = None, var_action: Action = None
):
    """

    @param spec_path:
    @param prefix:
    @param eos: NuSMV variable used to represent the end of a sequence
    @param var_action: NuSMV variable used to represent the current FSM state.
    @return:
    """
    if eos is None:
        eos = Action("_eos")

    if var_action is None:
        var_action = Action("_action")

    ltl_specs: List[LTLSpec] = []

    targets = dict()
    dev = parse(spec_path)
    for (src, dst) in dev.behaviors.as_list_tuples():
        dsts = targets.get(src, None)
        if dsts is None:
            evt = dev.events.find_by_name(src)
            targets[src] = dsts = Op.make(evt.is_final)
        dsts.add(dst)
    forms = []

    def mk_act(name):
        return And(Equal(var_action, Action(prefix + "_" + name)), Not(eos))

    def tau():
        return And(
            And.make(
                Not(Equal(var_action, Action(prefix + "_" + elem))) for elem in targets
            ),
            Not(eos),
        )

    for (src, op) in targets.items():
        args = list(map(mk_act, op.targets))
        if op.is_final:
            args.append(eos)
        will_happen = Or.make(args)
        f = Always(Implies(mk_act(src), Next(Until(tau(), will_happen))))
        forms.append(f)
    for f in forms:
        ltl_specs.append(LTLSpec(f))

    return ltl_specs


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    subparsers = parser.add_subparsers(
        dest="command", help="Each command performs some functionality regarding LTL"
    )
    subparsers.required = True
    i_parser = subparsers.add_parser(
        "instance",
        aliases=["i"],
        help="Generate the integration checks for a given instance.",
    )
    i_parser.add_argument(
        "--spec", "-s", type=Path, help="A Shelley specification", required=True
    )
    i_parser.add_argument("--name", "-n", help="The instance name", required=True)
    # Formula mode
    f_parser = subparsers.add_parser(
        "formula", aliases=["f"], help="Convert LTLf to NuSMV LTL"
    )
    f_parser.add_argument("formulas", nargs="+", help="LTLf formula")
    f_parser.add_argument("--name", "-n", help="Set an instance name")
    parser.add_argument(
        "--var-action",
        default="_action",
        help="NuSMV variable used to represent the current FSM state. Default: %(default)s",
    )
    parser.add_argument(
        "--var-end-of-sequence",
        default="_eos",
        help="NuSMV variable used to represent the end of a sequence. Default: %(default)s",
    )

    args = parser.parse_args()
    if args.command in ["i", "instance"]:
        ltl_specs: List[LTLSpec] = generate_spec(
            spec_path=args.spec,
            prefix=args.name,
            eos=Action(args.var_end_of_sequence),
            var_action=Action(args.var_action),
        )
        for spec in ltl_specs:
            print(spec)
    elif args.command in ["f", "formula"]:
        generate_formula(
            args.formulas,
            name=args.name,
            eos_var=Action(args.var_end_of_sequence),
            action_var=Action(args.var_action),
        )
