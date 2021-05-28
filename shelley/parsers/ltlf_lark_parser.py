from lark import Lark, Transformer
from dataclasses import dataclass


def binop(op) -> str:
    def to_str(self):
        return f"{paren(self.left)} {op} {paren(self.right)}"

    return to_str


def unop(op) -> str:
    def to_str(self):
        return f"{op} {paren(self.formula)}"

    return to_str


def paren(elem) -> str:
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
            result = arg
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
    return And(Implies(left, right), Implies(right, left))


def Releases(left, right):
    "If left never becomes true, right must remain true forever."
    return Not(Until(Not(left), Not(right)))


def WeakUntil(left, right):
    "Left must hold until right; right may never happen."


@dataclass
class ExistsFinally(Formula):
    """
    p is true in a state s0 if there exists a series of transitions 
    s_0 -> s_1, s_1 -> s_2, ...,s_{n−1} -> s_n such that p is true in s_n

    TODO: THIS IS A CTL FORMULA RATHER THAN LTLf!
    """

    formula: Formula
    __str__ = unop("EF")


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
        return Action("_".join(args))

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
