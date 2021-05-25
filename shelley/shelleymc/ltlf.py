from typing import List
from shelley.parsers import shelley_lark_parser
from pathlib import Path
from dataclasses import dataclass
from shelley.ast.devices import Device as ShelleyDevice
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


@dataclass
class Op:
    targets: list
    is_final: bool

    @classmethod
    def make(cls, is_final=False):
        return cls([], is_final)

    def add(self, name):
        self.targets.append(name)


def convert_ltlf_formulae(
        ltlf_formulas: List[str], name: str, eos: Action = None, var_action: Action = None
):
    """
    Convert LTLf to NuSMV LTL

    @param ltlf_formulas:
    @param name:
    @param eos:
    @param var_action:
    @return:
    """
    if eos is None:
        eos = Action("_eos")

    if var_action is None:
        var_action = Action("_action")

    ltl_formulae: List[str] = []

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

    for formula in ltlf_formulas:
        tree = ltlf_parser.parse(formula)
        ltlf = ltlf_parser.LTLParser().transform(tree)
        ltl_formulae.append(
            f"LTLSPEC {ltlf2ltl(ltlf, name=name, eos_var=eos, action_var=var_action)}"
        )

    return ltl_formulae


def generate_system_spec(spec: Path, eos: Action = None, var_action: Action = None
                         ):
    """

    @param spec:
    @param prefix:
    @param eos: NuSMV variable used to represent the end of a sequence
    @param var_action: NuSMV variable used to represent the current FSM state.
    @return:
    """

    if eos is None:
        eos = Action("_eos")

    if var_action is None:
        var_action = Action("_action")

    dev: ShelleyDevice = shelley_lark_parser.parse(spec)

    def and_ops(operations):
        print(operations)
        if len(operations) == 1:
            return Eventually(And(Equal(var_action, Action(operations[0])), Not(eos)))

        else:
            return And(Eventually(And(Equal(var_action, Action(operations[0])), Not(eos))), and_ops(operations[1:]))

    operations: List[str] = dev.events.list_str()
    ltl_spec: str = f"LTLSPEC {and_ops(operations)} ;"

    return ltl_spec


def generate_instance_spec(
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

    ltl_specs: List[str] = []

    targets = dict()
    dev: ShelleyDevice = shelley_lark_parser.parse(spec_path)
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
        ltl_specs.append(f"LTLSPEC {f} ;")

    return ltl_specs


def parse_command():
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

    return parser.parse_args()


def main():
    args = parse_command()
    if args.command in ["i", "instance"]:
        ltl_specs: List[str] = generate_instance_spec(
            spec_path=args.spec,
            prefix=args.name,
            eos=Action(args.var_end_of_sequence),
            var_action=Action(args.var_action),
        )
        for spec in ltl_specs:
            print(spec)
    elif args.command in ["f", "formula"]:
        ltl_formulae: List[str] = convert_ltlf_formulae(
            args.formulas,
            name=args.name,
            eos=Action(args.var_end_of_sequence),
            var_action=Action(args.var_action),
        )
        for formula in ltl_formulae:
            print(formula)
