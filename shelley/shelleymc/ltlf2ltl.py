from shelley.parsers.ltlf_lark_parser import (
    Bool,
    Action,
    And,
    Equal,
    Not,
    Or,
    Eventually,
    Implies,
    Next,
    Always,
    Until,
)


def convert(formula, name, eos_var, action_var):
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
