from __future__ import annotations
from typing import Dict

from shelley.ast.visitors import Visitor
from shelley.ast.devices import Device
from shelley.ast.actions import Action, Actions
from shelley.ast.events import Event, Events
from shelley.ast.behaviors import Behavior, Behaviors
from shelley.ast.components import Component, Components
from shelley.ast.triggers import Trigger, Triggers
from shelley.ast.rules import (
    TriggerRuleSequence,
    TriggerRuleChoice,
    TriggerRuleEvent,
    TriggerRuleFired,
)


class CheckWFSyntaxVisitor(Visitor):
    device: Device
    declared_devices: Dict[str, Device]

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
        element.check(
            self.device.uses,
            self.declared_devices,
            self.device.components.get_device_name(element.name),
        )

    def visit_trigger(self, element: Trigger) -> None:
        element.trigger_rule.accept(self)

    def visit_triggers(self, element: Triggers) -> None:
        for e in element.list():
            e.accept(self)

    def visit_components(self, element: Components) -> None:
        for e in element.list():
            e.accept(self)

    def visit_behaviour(self, element: Behavior) -> None:
        pass

    def visit_behaviors(self, element: Behaviors) -> None:
        for e in element.list():
            e.accept(self)

    def visit_action(self, element: Action) -> None:
        pass

    def visit_actions(self, element: Actions) -> None:
        for e in element.list():
            e.accept(self)

    def visit_event(self, element: Event) -> None:
        pass

    def visit_events(self, element: Events) -> None:
        pass

    def visit_device(self, element: Device) -> None:
        element.actions.accept(self)
        element.events.accept(self)
        element.behaviors.accept(self)
        element.components.accept(self)
        element.triggers.accept(self)
