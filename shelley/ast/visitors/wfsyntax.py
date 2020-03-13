from __future__ import annotations
from typing import Dict, Set

from . import Visitor
from shelley.ast.devices import Device
from shelley.ast.actions import Action
from shelley.ast.events import EEvent, IEvent
from shelley.ast.behaviours import Behaviour
from shelley.ast.components import Component
from shelley.ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, TriggerRuleFired


class CheckWFSyntaxVisitor(Visitor):
    device = None  # type: Device
    declared_devices = None  # type: Dict[str, Device]

    def __init__(self, device: Device, declared_devices: Dict[str, Device]):
        self.device = device
        self.declared_devices = declared_devices

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

    def visit_behaviour(self, element: Behaviour) -> None:
        pass
        # element.check(self.actions, self.ievents + self.eevents, self.behaviours)

    def visit_action(self, element: Action) -> None:
        pass

    def visit_ievent(self, element: IEvent) -> None:
        pass

    def visit_eevent(self, element: EEvent) -> None:
        pass

    def visit_device(self, element: Device) -> None:
        for a in element.actions:
            a.accept(self)
        for e in element.get_all_events():
            e.accept(self)
        for b in element.behaviours:
            b.accept(self)
        for c in element.components:
            c.accept(self)
        for trigger_event in element.triggers.keys():
            # TODO: check if event is declared
            rule = element.triggers[trigger_event]
            rule.accept(self)
