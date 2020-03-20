from __future__ import annotations

from . import Visitor
from shelley.ast.devices import Device
from shelley.ast.actions import Action, Actions
from shelley.ast.events import EEvent, IEvent, EEvents, IEvents
from shelley.ast.behaviors import Behavior, Behaviors
from shelley.ast.components import Component, Components
from shelley.ast.triggers import Trigger, Triggers
from shelley.ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, TriggerRuleFired


class TriggersVisitor(Visitor):
    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        pass

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        pass

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        pass

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
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

    def visit_ievent(self, element: IEvent) -> None:
        pass

    def visit_ievents(self, element: IEvents) -> None:
        pass

    def visit_eevent(self, element: EEvent) -> None:
        pass

    def visit_eevents(self, element: EEvents) -> None:
        pass

    def visit_device(self, element: Device) -> None:
        pass
