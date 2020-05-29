from __future__ import annotations
from typing import Optional

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


class PrettyPrintVisitor(Visitor):
    components: Components
    result: str

    def __init__(self, components: Optional[Components] = None):
        if components is None:
            components = Components()
        self.components = components
        self.result = ""

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        self.result += "fired"

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        self.result += "{0}.{1} ".format(element.component.name, element.event)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        # self.result += "( "
        element.left_trigger_rule.accept(self)
        self.result += "; "
        element.right_trigger_rule.accept(self)
        # self.result += ") "

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        self.result += "( "
        for rule in element.choices[0:-1]:
            rule.accept(self)
            self.result += "xor "
        element.choices[-1].accept(self)
        self.result += ") "

    def visit_trigger(self, element: Trigger) -> None:
        self.result += "    {0}: ".format(element.event.name)
        element.trigger_rule.accept(self)
        self.result = self.result.strip()
        self.result += "\n"

    def visit_triggers(self, element: Triggers) -> None:
        for trigger in element.list():
            trigger.accept(self)
        self.result += "\n"

    def visit_component(self, element: Component) -> None:
        device_name = self.components.get_device_name(element.name)
        self.result += "{0} {1}, ".format(device_name, element.name)

    def visit_components(self, element: Components) -> None:
        self.result += "  components:\n    "
        for component in element.list():
            component.accept(self)
        self.result = self.result[:-2]  # remove extra ", "
        self.result += "\n"

    def visit_behaviour(self, element: Behavior) -> None:
        if element.action is not None:
            self.result += "    {0} -> {1}() {2}\n".format(
                element.e1.name, element.action.name, element.e2.name
            )
        else:
            self.result += "    {0} -> {1}\n".format(element.e1.name, element.e2.name)

    def visit_behaviors(self, element: Behaviors) -> None:
        for behaviour in element.list():
            behaviour.accept(self)

    def visit_action(self, element: Action) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_actions(self, element: Actions) -> None:
        self.result += "  actions:\n    "
        for action in element.list():
            action.accept(self)
        self.result = self.result[:-2]  # remove extra ", "
        self.result += "\n"

    def visit_event(self, element: Event) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_events(self, element: Events) -> None:
        self.result += "  events:\n    "
        for event in element.list():
            event.accept(self)
        self.result = self.result[:-2]  # remove extra ", "
        self.result += "\n"

    def visit_device(self, element: Device) -> None:
        self.result = "\n"
        if len(element.uses) > 0:
            uses_str = ""
            for device_name in element.uses:
                uses_str += device_name + ", "
            self.result += "Device {0} uses {1}:\n".format(
                element.name, uses_str[0:-2]
            )  # remove extra ", "
        else:
            self.result += "Device {0}:\n".format(element.name)

        if len(element.actions) > 0:
            element.actions.accept(self)

        if len(element.events) > 0:
            element.events.accept(self)

        self.result += "  start events:\n    "
        start_events_str = ""
        for event in element.events.start_events():
            start_events_str += event.name + ", "
        self.result += "{}\n".format(start_events_str[0:-2])  # remove extra ", "

        self.result += "  final events:\n    "
        final_events_str = ""
        for event in element.events.final_events():
            final_events_str += event.name + ", "
        self.result += "{}\n".format(final_events_str[0:-2])  # remove extra ", "

        self.result += "  behaviours:\n"
        element.behaviors.accept(self)

        if len(element.components) > 0:
            element.components.accept(self)

        self.result += "  triggers:\n"
        element.triggers.accept(self)

    def __str__(self) -> str:
        return self.result
