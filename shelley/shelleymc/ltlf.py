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
)
from shelley.parsers.ltlf_lark_parser import parser as ltlf_parser
from shelley.shelleymc import ltlf2ltl


def generate_formula(formulas, name, eos_var, action_var):
    for formula in formulas:
        tree = ltlf_parser.parse(formula)
        ltlf = ltlf_parser.LTLParser().transform(tree)
        print(
            "LTLSPEC",
            ltlf2ltl.convert(ltlf, name=name, eos_var=eos_var, action_var=action_var,),
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


def generate_spec(spec_path: Path, prefix, eos, var_action):
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
        print("LTLSPEC", f, ";")


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
        generate_spec(
            spec_path=args.spec,
            prefix=args.name,
            eos=Action(args.var_end_of_sequence),
            var_action=Action(args.var_action),
        )
    elif args.command in ["f", "formula"]:
        generate_formula(
            args.formulas,
            name=args.name,
            eos_var=Action(args.var_end_of_sequence),
            action_var=Action(args.var_action),
        )
