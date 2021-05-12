
from shelley.parser import parse
from lark import Lark, Transformer

from dataclasses import dataclass

def binop(op):
    def to_str(self):
        return f"{paren(self.left)} {op} {paren(self.right)}"
    return to_str
def unop(op):
    def to_str(self):
        return f"{op} {paren(self.formula)}"
    return to_str
def paren(elem):
    if isinstance(elem, Bool) or isinstance(elem, Action):
        return str(elem)
    else:
        return "(" + str(elem) + ")"

@dataclass
class Formula:
    pass

def fold(op, zero, args):
    result = None
    for arg in args:
        if result is None:
            result =  arg
        else:
            result = op(result, arg)
    if result is None:
        return zero
    else:
        return result

@dataclass
class And(Formula):
    left: Formula
    right: Formula
    __str__ = binop("&")
    @classmethod
    def make(cls, args):
        return fold(cls, Bool(True), args)

@dataclass
class Equal(Formula):
    left: Formula
    right: Formula
    __str__ = binop("=")

@dataclass
class Or(Formula):
    left: Formula
    right: Formula
    __str__ = binop("|")
    @classmethod
    def make(cls, args):
        return fold(cls, Bool(True), args)

@dataclass
class Not(Formula):
    formula: Formula
    __str__ = unop("!")

@dataclass
class Bool(Formula):
    value: bool
    def __str__(self):
        return "TRUE" if self.value else "FALSE"

@dataclass
class Action(Formula):
    name: str
    def __str__(self):
        return self.name

@dataclass
class Next(Formula):
    "Must be true in the following step."
    formula: Formula
    __str__ = unop("X")

@dataclass
class Until(Formula):
    "Left must happen until right happens; right will eventually happen."
    left: Formula
    right: Formula
    __str__ = binop("U")

def Last():
    "The last instance of a trace"
    return Not(Next(Bool(True)))

def WeakNext(formula):
    "The given formula must hold unless it is last."
    return Not(Next(Not(formula)))

@dataclass
class Eventually(Formula):
    "The formula will eventually hold"
    formula: Formula
    __str__ = unop("F")

# def Eventually(formula):
#     "The formula will eventually hold"
#     return Until(Bool(True), formula)

@dataclass
class Always(Formula):
    "The formula holds at every step of the trace"
    formula: Formula
    __str__ = unop("G")

# def Always(formula):
#     "The formula holds at every step of the trace"
#     return Not(Eventually(Not(formula)))

@dataclass
class Implies(Formula):
    left: Formula
    right: Formula
    __str__ = binop("->")

def Equiv(left, right):
    "Logical equivalence"
    return And(
        Implies(left, right),
        Implies(right, left)
    )

def Releases(left, right):
    "If left never becomes true, right must remain true forever."
    return Not(Until(Not(left), Not(right)))

def WeakUntil(left, right):
    "Left must hold until right; right may never happen."


def ltlf_to_ltl(formula, name, eos_var, action_var):
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
                left=rec(formula.left),
                right=And(rec(formula.right), Not(eos_var))
            )
        raise TypeError(formula)
    return rec(formula)

parser = Lark(r"""
formula:
    | last
    | atom
    | paren
    | land
    | lor
    | lnot
    | implies
    | equiv
    | next
    | next
    | until
    | globally
    | eventually
    | eq
atom:
    | bool
    | act
ident: CNAME
act: (ident ".")? ident

true: "true"
false: "false"
bool: true | false

paren: "(" formula ")"
land: formula "&" formula
lor: formula "|" formula
lnot: "!" formula
next: "X" formula
until: formula "U" formula
implies: formula "->" formula
equiv: formula "<->" formula
globally: "G" formula
eventually: "F" formula
last: "L"
eq: atom "=" atom
%import common.CNAME
%import common.WS
%ignore WS
""", start="formula")

class LTLParser(Transformer):
    def true(self, args):
        return True
    def false(self, args):
        return False
    def bool(self, args):
        return Bool(args[0])
    def paren(self, args):
        return args[0]
    def land(self, args):
        return And(*args)
    def formula(self, args):
        return args[0]
    def next(self, args):
        return Next(*args)
    def ident(self, args):
        return args[0].value
    def act(self, args):
        return Action("_".join(args))
    def lor(self, args):
        return Or(*args)
    def lnot(self, args):
        return Not(*args)
    def until(self, args):
        return Until(*args)
    def implies(self, args):
        return Implies(*args)
    def equiv(self, args):
        return Equiv(*args)
    def globally(self, args):
        return Always(*args)
    def eventually(self, args):
        return Eventually(*args)
    def last(self, args):
        return Last()
    def eq(self, args):
        return Equal(*args)
    def atom(self, args):
        return args[0]

@dataclass
class Op:
    targets: list
    is_final: bool
    @classmethod
    def make(cls, is_final=False):
        return cls([], is_final)
    def add(self, name):
        self.targets.append(name)

def generate_spec(filename, prefix, eos):
    targets = dict()
    dev = parse(open(filename))
    for (src, dst) in dev.behaviors.as_list_tuples():
        dsts = targets.get(src, None)
        if dsts is None:
            evt = dev.events.find_by_name(src)
            targets[src] = dsts = Op.make(evt.is_final)
        dsts.add(dst)
    forms = []
    def mk_act(name):
        return And(
            Equal(Action("action"), Action(prefix + "_" + name)),
            Not(eos)
        )
    def tau():
        return And(
            And.make(
                Not(Equal(Action("action"), Action(prefix + "_" + elem)))
                for elem in targets
            ),
            Not(eos)
        )

    for (src, op) in targets.items():
        args = list(map(mk_act, op.targets))
        if op.is_final:
            args.append(eos)
        will_happen = Or.make(args)
        f = Always(
            Implies(mk_act(src), Next(Until(tau(), will_happen)))
        )
        forms.append(f)
    for f in forms:
        print("LTLSPEC", f, ";")
def generate_formula(formulas, name, eos_var, action_var):
    for formula in formulas:
        tree = parser.parse(formula)
        #print(repr(LTLParser().transform(tree)))
        print(
            ltlf_to_ltl(
                LTLParser().transform(tree),
                name=name,
                eos_var=eos_var,
                action_var=action_var
            )
        )

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", help="Each command performs some functionality regarding LTL")
    subparsers.required = True
    i_parser = subparsers.add_parser("instance", aliases=["i"], help="Generate the integration checks for a given instance.")
    i_parser.add_argument("--spec", "-s", help="A Shelley specification", required=True)
    i_parser.add_argument("--name", "-n", help="The instance name", required=True)
    # Formula mode
    f_parser = subparsers.add_parser("formula", aliases=["f"], help="Convert LTLf to NuSMV LTL")
    f_parser.add_argument("formulas", nargs="+", help="LTLf formula")
    f_parser.add_argument("--name", "-n", help="Set an instance name")
    parser.add_argument("--var-action", default="ACTION", help="NuSMV variable used to represent the current FSM state. Default: %(default)s")
    parser.add_argument("--var-end-of-sequence", default="END", help="NuSMV variable used to represent the end of a sequence. Default: %(default)s")

    args = parser.parse_args()
    if args.command in ["i", "instance"]:
        generate_spec(filename=args.spec, prefix=args.name, eos=Action(args.var_end_of_sequence))
    elif args.command in ["f", "formula"]:
        generate_formula(
            args.formulas,
            name=args.name,
            eos_var=Action(args.var_end_of_sequence),
            action_var=Action(args.var_action)
        )
