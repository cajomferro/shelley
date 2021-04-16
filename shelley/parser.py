import copy
from lark import Lark, Transformer
from shelley.ast.rules import (
    TriggerRule,
    TriggerRuleEvent,
    TriggerRuleChoice,
    TriggerRuleSequence,
    TriggerRuleFired,
)
from shelley.ast.triggers import Trigger, Triggers, TriggersListDuplicatedError
from shelley.ast.components import Components
from shelley.ast.events import Event, Events
from shelley.ast.behaviors import Behaviors, BehaviorsListDuplicatedError
from shelley.ast.devices import Device

INITIAL = 1
FINAL = 2

parser = Lark(r"""

expr:
  | call
  | choice
  | loop
  | seq

block: "{" expr "}" -> expr

call: ident "." ident ";"

seq: expr expr

choice: block "+" block

loop: "loop" block

modifier : initial | final
initial : "initial"
final : "final"
modifiers:
  | initial
  | final
  | initial final
  | final initial

ident: CNAME

next: ("->" ident)* -> next_evts

sig:  [modifiers] ident next

op : sig block

ops : "{" op+ "}"

key_val: ident ":" ident
key_vals: [key_val ("," key_val)* [","]]

sys:
| ident "(" key_vals ")" ops -> new_sys
| "abstract"  ident "{" sig+ "}" -> abs_sys

%import common.CNAME
%import common.WS
%ignore WS

    """, start='sys')

class ShelleyLanguage(Transformer):
    def seq(self, args):
        return TriggerRuleSequence(*args)

    def call(self, args):
        return TriggerRuleEvent(*args)

    def choice(self, args):
        choice = TriggerRuleChoice()
        choice.choices.extend(args)
        return choice

    def expr(self, args):
        if len(args) != 1:
            return None
        return args[0]

    def key_val(self, args):
        return args

    def key_vals(self, kv):
        result = Components()
        for (k, v) in kv:
            result.create(k, v)
        return result

    def sig(self, args):
        modifiers, name, nxt = args
        return Event(
            name=name,
            is_start=INITIAL in modifiers,
            is_final=FINAL in modifiers,
        ), nxt

    def initial(self, args):
        return INITIAL

    def final(self, args):
        return FINAL

    def modifiers(self, args):
        return args

    def next_evts(self, args):
        return args

    def op(self, args):
        (evt,nxt), code = args
        return (evt, nxt, Trigger(copy.copy(evt), code))

    def ops(self, args):
        evts = Events()
        triggers = Triggers()
        behaviors = Behaviors()
        for evt, nxt, code in args:
            triggers.add(code)
            for n in nxt:
                behaviors.create(copy.copy(evt), Event(name=n, is_start=False, is_final=True))
            evts.add(evt)

        return evts, triggers, behaviors

    def ident(self, args):
        name, = args
        return name.value

    def new_sys(self, args):
        # CNAME "(" key_vals ")" ops
        name, components, (evts, triggers, behaviors) = args
        device = Device(name=name,
            events=evts,
            behaviors=behaviors,
            triggers=triggers,
            components=components,
        )

        device.test_macro = dict()
        device.test_micro = dict()

        return device

    def abs_sys(self, args):
        name, *sigs = args
        events = Events()
        triggers = Triggers()
        behaviors = Behaviors()
        for (evt, nxt) in sigs:
            for n in nxt:
                behaviors.create(copy.copy(evt), Event(name=n, is_start=False, is_final=True))
            events.add(evt)
            triggers.create(evt, TriggerRuleFired())

        device =  Device(
            name=name,
            events=events,
            behaviors=behaviors,
            triggers=triggers,
        )

        device.test_macro = dict()
        device.test_micro = dict()

        return device


def main():

    LED = """
    abstract Led {
    initial final on -> off

    initial final off -> on
    }
    """

    COMPLICATED = """
    Controller(v1:Valve,
        v2: Valve,
        v3: Valve,
        v4: Valve,
        m: Magnetic,
        r: RadioV1,
        lp: LowPower) {

        initial final start -> activateAllValves {
            { m.locked; m.unlocked;}
            +
            { lp.wakeup; }
        }

        final update -> deactivateAllValves {
            r.start;
            r.HTTPsetup;
            r.HTTPconnect;
            r.HTTPsend;
            r.HTTPreceive;
            r.HTTPdisconnect;
            r.HTTPdisable;
        }

        final activateAllValves -> update {
            v1.on; v2.on; v3.on; v4.on;
        }

        final deactivateAllValves -> sleep {
            v1.off; v2.off; v3.off; v4.off;
        }

        final sleep -> start {
            { lp.setup;lp.sleep;} + {lp.sleep;}
        }
    }

    """

    CODE = """
            { m.locked; m.unlocked;}
            +
            { lp.wakeup; }
    """
    import sys
    tree = parser.parse(open(sys.argv[1]).read())
    print(ShelleyLanguage().transform(tree))
