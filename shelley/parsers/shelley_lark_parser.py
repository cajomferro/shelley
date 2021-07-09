import copy
from lark import Lark, Transformer
from shelley.ast.rules import (
    TriggerRule,
    TriggerRuleEvent,
    TriggerRuleChoice,
    TriggerRuleSequence,
    TriggerRuleFired,
)
from shelley.parsers import errors
from pathlib import Path
from shelley.ast.triggers import Trigger, Triggers, TriggersListDuplicatedError
from shelley.ast.components import Components
from shelley.ast.events import Event, Events
from shelley.ast.behaviors import Behaviors, BehaviorsListDuplicatedError
from shelley.ast.devices import Device
from shelley.parsers.ltlf_lark_parser import LTLParser

INITIAL = 1
FINAL = 2

parser = Lark.open("shelley_grammar.lark", rel_to=__file__, start="sys")


class ShelleyLanguage(LTLParser):
    def seq(self, args):
        return TriggerRuleSequence(*args)

    def call(self, args):
        c_name, e_name = args
        component = self.components[c_name]
        return TriggerRuleEvent(component, e_name)

    def choice(self, args):
        if len(args) != 1:
            choice = TriggerRuleChoice()
            choice.choices.extend(args)
            return choice
        else:
            return args[0]

    def expr(self, args):
        if len(args) != 1:
            return None
        return args[0]

    def name_type(self, args):
        return args

    def uses(self, name_type):

        self.components = Components()
        for (name, type) in name_type:
            self.components.create(name, type)
        return self.components

    def sig(self, args):
        modifiers, name, nxt = args
        return (
            Event(
                name=name, is_start=INITIAL in modifiers, is_final=FINAL in modifiers,
            ),
            nxt,
        )

    def sigs(self, args):
        return args

    def enforce(self, args):
        return args

    def initial(self, args):
        return INITIAL

    def final(self, args):
        return FINAL

    def modifiers(self, args):
        return args

    def next_evts(self, args):
        return args

    def op(self, args):
        (evt, nxt), code = args
        return (evt, nxt, Trigger(copy.copy(evt), code))

    def ops(self, args):
        evts = Events()
        triggers = Triggers()
        behaviors = Behaviors()
        for evt, nxt, code in args:
            triggers.add(code)
            if len(nxt) > 0:
                for n in nxt:
                    behaviors.create(
                        copy.copy(evt),
                        # at this point we don't know the initial/final modifiers for the operation on the right side
                        Event(name=n, is_start=False, is_final=True),
                    )
            else:
                behaviors.create(copy.copy(evt))  # operation without next operations
            evts.add(evt)

        for beh in behaviors:
            if not beh.e1.is_final and beh.e2 is None:
                # a non-final operation without next operations is a sink
                raise ValueError(
                    f"{errors.WFORMED_NON_FINAL_LEFT_OPERATION_WITHOUT_RIGHT_SIDE(beh.e1.name)}"
                )

            if beh.e2 is not None:
                operation = evts.find_by_name(beh.e2.name)
                if operation is None:
                    # make sure that all operations on the right side are also declared on the left
                    raise ValueError(
                        f"{errors.WFORMED_UNDECLARED_OPERATION_RIGHT_SIDE(beh.e1.name, beh.e2.name)}"
                    )
                else:
                    # updates the initial/final modifiers for the operation on the right side (e2)
                    beh.e2.is_start = operation.is_start
                    beh.e2.is_final = operation.is_final

        return evts, triggers, behaviors

    def ident(self, args):
        (name,) = args
        return name.value

    def new_sys(self, args):
        name, components, (evts, triggers, behaviors), enforce = args

        device = Device(
            name=name,
            events=evts,
            behaviors=behaviors,
            triggers=triggers,
            components=components,
        )

        device.test_macro = dict()
        device.test_micro = dict()

        return device

    def base_sys(self, args):
        name, sigs, enforce = args
        events = Events()
        triggers = Triggers()
        behaviors = Behaviors()
        for (evt, nxt) in sigs:
            if len(nxt) > 0:
                for n in nxt:
                    behaviors.create(
                        copy.copy(evt), Event(name=n, is_start=False, is_final=True)
                    )
            else:
                behaviors.create(copy.copy(evt))  # operation without next operations
            events.add(evt)
            triggers.create(evt, TriggerRuleFired())

        for beh in behaviors:
            if not events.find_by_name(beh.e2.name):
                raise ValueError(
                    f"{errors.WFORMED_UNDECLARED_OPERATION_RIGHT_SIDE(beh.e1.name, beh.e2.name)}"
                )

        device = Device(
            name=name, events=events, behaviors=behaviors, triggers=triggers,
        )

        # device.test_macro = dict()
        # device.test_micro = dict()
        if len(enforce) > 0:
            device.enforce_formulae = enforce

        return device


def parse(source: Path):
    with Path.open(source) as fp:
        tree = parser.parse(fp.read())
    return ShelleyLanguage().transform(tree)


def main():
    import sys

    if len(sys.argv) < 2:
        print("Please provide a valid source path! Usage: lark2shelley PATH")
        sys.exit(255)
    print(parse(Path(sys.argv[1])))


if __name__ == "__main__":
    main()
