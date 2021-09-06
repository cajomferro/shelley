from __future__ import annotations

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
    TriggerRuleLoop,
    TriggerRuleEvent,
    TriggerRuleFired,
)


class TriggersVisitor(Visitor):
    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        pass

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        pass

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        pass

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        pass

    def visit_trigger_rule_loop(self, element: TriggerRuleLoop) -> None:
        pass

    def visit_trigger(self, element: Trigger) -> None:
        pass

    def visit_triggers(self, element: Triggers) -> None:
        pass

    def visit_component(self, element: Component) -> None:
        pass

    def visit_components(self, element: Components) -> None:
        pass

    def visit_behaviour(self, element: Behavior) -> None:
        pass

    def visit_behaviors(self, element: Behaviors) -> None:
        pass

    def visit_action(self, element: Action) -> None:
        pass

    def visit_actions(self, element: Actions) -> None:
        pass

    def visit_event(self, element: Event) -> None:
        pass

    def visit_events(self, element: Events) -> None:
        pass

    def visit_device(self, element: Device) -> None:
        pass
