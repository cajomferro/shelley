from lark import Lark, Transformer
from dataclasses import dataclass, field
from io import StringIO
from typing import List, Optional, IO

@dataclass
class Formula:
    pass

@dataclass
class Atomic(Formula):
    pass

@dataclass
class BinaryOperator:
    left: Formula
    right: Formula


@dataclass
class UnaryOperator:
    child: Formula


@dataclass
class CTL(Formula):
    formula: Formula

@dataclass
class LTL(Formula):
    formula: Formula

@dataclass
class LTL_F(Formula):
    formula: Formula


def fold(op, zero, args):
    result = None
    for arg in args:
        if result is None:
            result = arg
        else:
            result = op(result, arg)
    if result is None:
        return zero
    else:
        return result

# Atoms

@dataclass
class Bool(Atomic):
    value: bool

@dataclass
class Variable(Atomic):
    name: str

@dataclass
class Action(Atomic):
    name: str
    prefix: Optional[str] = field(default=None)

@dataclass
class NotAction(Atomic):
    name: str
    prefix: Optional[str] = field(default=None)

# Specific to LTLF

@dataclass
class EndOfSequence(Atomic):
    pass

EOS = EndOfSequence()

# Propositional logic

@dataclass
class Not(UnaryOperator):
    operator = "!"

@dataclass
class And(BinaryOperator):
    operator = "&"

    @classmethod
    def make(cls, args):
        return fold(cls, Bool(True), args)

@dataclass
class Equal(BinaryOperator):
    operator = "="

@dataclass
class Or(BinaryOperator):
    operator = "|"

    @classmethod
    def make(cls, args):
        return fold(cls, Bool(True), args)

@dataclass
class Implies(BinaryOperator):
    operator = "->"

# Linear Temporal Logic



@dataclass
class Next(UnaryOperator):
    operator = "X"
    "Must be true in the following step."

@dataclass
class Eventually(UnaryOperator):
    "The formula will eventually hold"
    operator = "F"

@dataclass
class Always(UnaryOperator):
    "The formula holds at every step of the trace"
    operator = "G"

@dataclass
class Until(BinaryOperator):
    "Left must happen until right happens; right will eventually happen."
    operator = "U"


# CTL

@dataclass
class ExistsFinally(UnaryOperator):
    """
    p is true in a state s0 if there exists a series of transitions 
    s_0 -> s_1, s_1 -> s_2, ...,s_{n−1} -> s_n such that p is true in s_n

    TODO: THIS IS A CTL FORMULA RATHER THAN LTLf!
    """
    operator = "EF"

# Abbreviations

def Last():
    "The last instance of a trace"
    return Not(Next(Bool(True)))


def WeakNext(formula):
    "The given formula must hold unless it is last."
    return Not(Next(Not(formula)))


def Equiv(left, right):
    "Logical equivalence"
    return And(Implies(left, right), Implies(right, left))


def Releases(left, right):
    "If left never becomes true, right must remain true forever."
    return Not(Until(Not(left), Not(right)))

# Conversions

def ltlf_to_ltl(formula:Formula, eos:Variable, action:Variable, prefix_separator="_") -> Formula:
    """
    Converts an LTLf formula in an LTL formula
    """
    def rec(formula, mode=LTL_F):
        while type(formula) in (LTL, CTL, LTL_F):
            mode = type(formula)
            formula = formula.formula

        if mode is LTL or mode is CTL:
            if isinstance(formula, Atomic):
                if not (isinstance(formula, Bool) or isinstance(formula, Variable)):
                    raise ValueError(f"Expecting an atomic {mode.__name__} formula, but got: ", formula)
                return formula
            elif isinstance(formula, UnaryOperator):
                return type(formula)(rec(formula.child, mode=mode))
            elif isinstance(formula, BinaryOperator):
                return type(formula)(rec(formula.left, mode=mode), rec(formula.right, mode=mode))

        assert mode is LTL_F

        if isinstance(formula, Bool) or isinstance(formula, Variable):
            return formula
        elif isinstance(formula, NotAction) or isinstance(formula, Action):
            if formula.prefix is None:
                name = formula.name
            else:
                name = formula.prefix + prefix_separator + formula.name
            act = Equal(action, Variable(name))
            return And(
                Not(act) if isinstance(formula, NotAction) else act,
                Not(rec(EOS))
            )
        elif isinstance(formula, EndOfSequence):
            return eos
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
            return Next(And(rec(formula.formula), Not(rec(EOS))))
        elif isinstance(formula, Eventually):
            return Eventually(And(rec(formula.formula), Not(rec(EOS))))
        elif isinstance(formula, Always):
            return Always(Or(rec(formula.formula), rec(EOS)))
        elif isinstance(formula, Until):
            return Until(
                left=rec(formula.left),
                right=And(
                    rec(formula.right),
                    Not(rec(EOS))
                )
            )
        else:
            raise ValueError(type(formula), formula, mode)

    return rec(formula)


def dump(formula:Formula, fp:IO, eos=None, nusvm_strict=True):
    """
    Converts a formula into an NuSMV string
    """
    def rec(formula):
        # Primitives
        if isinstance(formula, Bool):
            fp.write("TRUE" if self.value else "FALSE")
        elif isinstance(formula, Variable):
            fp.write(formula.name)
        elif isinstance(formula, Action):
            if nusvm_strict:
                raise ValueError(formula)
            if formula.prefix is not None:
                fp.write(formula.prefix)
                fp.write(".")
            fp.write(formula.name)
        elif isinstance(formula, EndOfSequence):
            if nusvm_strict:
                raise ValueError(formula)
            fp.write(eos if eos is not None else "ε")

        elif isinstance(formula, UnaryOperator):
            # Operator
            fp.write(formula.operator)
            fp.write(' ')
            # Child
            if isinstance(formula.child, Atomic):
                rec(formula.child)
            else:
                fp.write('(')
                rec(formula.child)
                fp.write(')')

        elif isinstance(formula, BinaryOperator):
            # Left
            if isinstance(formula.left, Atomic):
                rec(formula.left)
            else:
                fp.write('(')
                rec(formula.left)
                fp.write(')')
            # Operator
            fp.write(' ')
            fp.write(formula.operator)
            fp.write(' ')
            # Right
            if isinstance(formula.right, Atomic):
                rec(formula.right)
            else:
                fp.write('(')
                rec(formula.right)
                fp.write(')')
        else:
            raise ValueError(type(formula), formula)
    # Recursive call
    rec(formula)

def dumps(formula, eos=None, nusvm_strict=True):
    buffer = StringIO()
    dump(
        formula=formula,
        fp=buffer,
        eos=eos,
        eos_variable=eos_variable,
    )
    return buffer.getvalue()

parser = Lark.open("ltlf_grammar.lark", rel_to=__file__, start="formula")


class LTLParser(Transformer):
    def true(self, args) -> Bool:
        return True

    def false(self, args) -> Bool:
        return False

    def bool(self, args) -> Bool:
        return Bool(args[0])

    def paren(self, args):
        return args[0]

    def land(self, args) -> And:
        return And(*args)

    def formula(self, args):
        return args[0]

    def next(self, args) -> Next:
        return Next(*args)

    def ident(self, args):
        return args[0].value

    def act(self, args) -> Action:
        return Action(*args)

    def lor(self, args) -> Or:
        return Or(*args)

    def lnot(self, args) -> Not:
        return Not(*args)

    def until(self, args) -> Until:
        return Until(*args)

    def implies(self, args) -> Implies:
        return Implies(*args)

    def equiv(self, args) -> Equiv:
        return Equiv(*args)

    def globally(self, args) -> Always:
        return Always(*args)

    def eventually(self, args) -> Eventually:
        return Eventually(*args)

    def last(self, args) -> Last:
        return Last()

    def eq(self, args) -> Equal:
        return Equal(*args)

    def atom(self, args):
        return args[0]
