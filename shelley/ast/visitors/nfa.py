from __future__ import annotations
from typing import Dict, Set, Tuple, List

from . import Visitor
from shelley.ast.devices import Device
from shelley.ast.actions import Action
from shelley.ast.events import EEvent, IEvent
from shelley.ast.behaviors import Behavior
from shelley.ast.components import Component
from shelley.ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, TriggerRuleFired
from shelley.dfaapp.automaton import NFA


class CountStatesVisitor(Visitor):
    visited_events = None  # type: List[str]
    # state_names = None # type: List[Tuple[str, str, str]]
    state_names = None  # type: Dict
    counter = None  # type: int

    def __init__(self):
        self.counter = 1
        self.visited_events = []
        self.state_names = {0: []}

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        pass

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        pass

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        pass

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        pass

    def visit_component(self, element: Component) -> None:
        pass

    def visit_behaviour(self, element: Behavior) -> None:
        if element.e1.name not in self.visited_events and element.e2.name not in self.visited_events:
            self.visited_events.append(element.e1.name)
            self.visited_events.append(element.e2.name)
            #self.state_names.append("{0}_{1}".format(element.e1.name, element.e2.name))
            self.state_names[self.counter] = []
            self.state_names[self.counter].append(element.e1.name)
            self.counter += 1


    def visit_action(self, element: Action) -> None:
        pass

    def visit_ievent(self, element: IEvent) -> None:
        pass

    def visit_eevent(self, element: EEvent) -> None:
        pass

    def visit_device(self, element: Device) -> None:
        for b in element.behaviors:
            b.accept(self)


class CreateNFAVisitor(Visitor):
    device = None  # type: Device
    declared_devices = None  # type: Dict[str, Device]
    nfa = None  # type: NFA
    device_label = None  # type: str
    edges = None  # type: List[Tuple[int, List[str], int]]

    # def __init__(self, device: Device, declared_devices: Dict[str, Device]):
    #     self.device = device
    #     self.declared_devices = declared_devices

    def __init__(self, device_label: str):
        self.device_label = device_label

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        pass

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        element.check_wf_syntax(self.declared_devices, self.device.components)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_component(self, element: Component) -> None:
        element.check(self.device.uses, self.declared_devices, self.device.components[element])

    def visit_behaviour(self, element: Behavior) -> None:
        pass
        # element.check(self.actions, self.ievents + self.eevents, self.behaviours)

    def visit_action(self, element: Action) -> None:
        pass

    def visit_ievent(self, element: IEvent) -> None:
        pass

    def visit_eevent(self, element: EEvent) -> None:
        pass

    def visit_device(self, element: Device) -> None:

        alphabet = []
        for e in element.get_all_events():
            if e.name != 'begin':
                alphabet.append("{0}.{1}".format(self.device_label, e.name))
        for b in element.behaviors:
            b.accept(self)
        # for c in element.components:
        #     c.accept(self)
        # for trigger_event in element.triggers.keys():
        #     # TODO: check if event is declared
        #     rule = element.triggers[trigger_event]
        #     rule.accept(self)

        self.nfa = NFA(
            alphabet=alphabet,
            transition_func=NFA.transition_edges([
                (0, ["b.pressed"], 1),
                (1, ["b.released"], 0),
            ]),
            start_state=0,
            accepted_states=[0, 1],
        )
