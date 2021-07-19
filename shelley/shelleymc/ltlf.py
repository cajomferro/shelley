from typing import List, Union, Optional
from shelley.parsers import shelley_lark_parser, ltlf_lark_parser
from pathlib import Path
from dataclasses import dataclass

from shelley.ast.devices import Device
import shelley.parsers.ltlf_lark_parser
from shelley.parsers.ltlf_lark_parser import (
    Variable,
    And,
    Equal,
    Action,
    NotAction,
    Not,
    Always,
    Next,
    Implies,
    Or,
    Until,
    Bool,
    Eventually,
    ExistsFinally,
    Formula,
    ltlf_to_ltl,
    LTL,
    LTL_F,
    CTL,
    EOS,
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
class Spec:
    formulae: List[Union[CTL, LTL, LTL_F]]
    comment: Optional[str]
    def __len__(self):
        return len(self.formulae)

    def dump(self, fp, action_name:Optional[str]=None, eos_name:Optional[str]=None):
        action = Variable("_action" if action_name is None else action_name)
        eos = Variable("_eos" if eos_name is None else eos_name)
        if self.comment is not None:
            fp.write("-- ")
            fp.write(self.comment)
            fp.write("\n")

        for f in self.formulae:
            is_ctl = isinstance(f, CTL)
            f = ltlf_to_ltl(f, eos=eos, action=action)
            if is_ctl:
                fp.write("SPEC ")
            else:
                fp.write("LTLSPEC ")
            ltlf_lark_parser.dump(formula=f, fp=fp)
            fp.write("\n")

    def dumps(self, action_name:Optional[str]=None, eos_name:Optional[str]=None):
        buffer = StringIO()
        self.dump(
            fp=buffer,
            action_name=action_name,
            eos_name=eos_name,
        )
        return buffer.getvalue()

def generate_system_spec(dev: Device) -> Spec:
    """
    @param dev: Shelley device instance
    @return:
    """
    specs = []
    for op in dev.events.list_str():
        specs.append(CTL(ExistsFinally(
            And(
                LTL_F(Action(op)),
                ExistsFinally(LTL_F(EOS))
            )
        )))
    return Spec(specs, comment=f"SYSTEM VALIDITY FOR: {dev.name}")

def generate_usage_validity(dev:Device, prefix:Optional[str]) -> Spec:
    """
    Generates a spec that represents the usage validity of a given device.
    """
    mk_act = lambda name: LTL_F(Action(prefix=prefix, name=name))
    targets = dict()
    for (src, dst) in dev.behaviors.as_list_tuples():
        dsts = targets.get(src, None)
        if dsts is None:
            evt = dev.events.find_by_name(src)
            targets[src] = dsts = Op.make(evt.is_final)
        dsts.add(dst)

    if prefix is None:
        tau = None
    else:
        tau = LTL_F(And.make(
            NotAction(prefix=prefix, name=op) for op in targets
        ))
    lbl = "" if prefix is None else f"{prefix}: "
    spec = Spec(formulae=[], comment=f"USAGE VALIDITY FOR {lbl}{dev.name}")
    for (src, op) in targets.items():
        successors = Or.make(map(mk_act, op.targets))
        if op.is_final:
            successors = Or(successors, LTL_F(EOS))

        # If there is a prefix, then it means there might be other
        # actions from other prefixes which are fine to ignore.
        # We ignore prefixes from other with TAU
        if prefix is not None:
            successors = Until(tau, successors)

        spec.formulae.append(
            LTL(Always(Implies(mk_act(src), Next(successors))))
        )
    return spec

def generate_enforce_usage(dev:Device, prefix:Optional[str]) -> Spec:
    if prefix is None:
        lbl = ""
    else:
        lbl = f"{prefix}: "
    spec = Spec(formulae=[], comment=f"ENFORCE SPECS FOR {lbl}{dev.name}")
    for f in dev.enforce_formulae:
        spec.formulae.append(LTL_F(f))
    return spec


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
        dev: Device = shelley_lark_parser.parse(args.spec)
        ltl_specs: List[str] = generate_instance_spec(
            dev=dev,
            prefix=args.name,
            eos=Action(args.var_end_of_sequence),
            var_action=Action(args.var_action),
        )
        for spec in ltl_specs:
            print(spec)
    elif args.command in ["f", "formula"]:
        ltlf_formulae: List[Formula] = parse_ltlf_formulae(args.formulas)
        ltl_formulae: List[str] = convert_ltlf_formulae(
            ltlf_formulae,
            name=args.name,
            eos=Action(args.var_end_of_sequence),
            var_action=Action(args.var_action),
        )
        for formula in ltl_formulae:
            print(formula)
