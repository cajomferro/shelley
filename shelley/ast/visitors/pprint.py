from __future__ import annotations
from typing import Dict

from . import Visitor
from shelley.ast.devices import Device
from shelley.ast.actions import Action, Actions
from shelley.ast.events import EEvent, IEvent, EEvents, IEvents
from shelley.ast.behaviours import Behaviour, Behaviors
from shelley.ast.components import Component, Components
from shelley.ast.triggers import Trigger, Triggers
from shelley.ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, TriggerRuleFired


class PrettyPrintVisitor(Visitor):
    declared_devices = None  # type: Dict[str, Device]
    components = None  # type:Components
    result = None

    def __init__(self, components: Components = None, declared_devices: Dict[str, Device] = None):
        self.components = components
        self.declared_devices = declared_devices
        self.result = ""

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        self.result += "fired"

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        self.result += "{0}.{1} ".format(element.component.name, element.event.name)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        self.result += "( "
        element.left_trigger_rule.accept(self)
        self.result += " ; "
        element.right_trigger_rule.accept(self)
        self.result += ")"

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        self.result += "( "
        element.left_trigger_rule.accept(self)
        self.result += " xor "
        element.right_trigger_rule.accept(self)
        self.result += ")"

    def visit_trigger(self, element: Trigger) -> None:
        self.result += "    {0}: ".format(element.event.name)
        element.trigger_rule.accept(self)
        self.result += "\n"

    def visit_triggers(self, element: Triggers) -> None:
        for trigger in element._data:
            trigger.accept(self)
        self.result += "\n"

    def visit_component(self, element: Component) -> None:
        device_name = self.components.get_device_name(element.name)
        device = self.declared_devices[device_name]
        self.result += "{0} {1}, ".format(device.name, element.name)

    def visit_components(self, element: Components) -> None:
        self.result += "  components:\n    "
        for component in element._data:
            component.accept(self)
        self.result += "\n"

    def visit_behaviour(self, element: Behaviour) -> None:
        if element.action is not None:
            self.result += "    {0} -> {1}() {2}\n".format(element.e1.name, element.action.name, element.e2.name)
        else:
            self.result += "    {0} -> {1}\n".format(element.e1.name, element.e2.name)

    def visit_behaviors(self, element: Behaviors) -> None:
        for behaviour in element._data:
            behaviour.accept(self)

    def visit_action(self, element: Action) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_actions(self, element: Actions) -> None:
        self.result += "  actions:\n    "
        for action in element._data:
            action.accept(self)
        self.result += "\n"

    def visit_ievent(self, element: IEvent) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_ievents(self, element: IEvents) -> None:
        self.result += "  internal events:\n    "
        for event in element._data:
            event.accept(self)
        self.result += "\n"

    def visit_eevent(self, element: EEvent) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_eevents(self, element: EEvents) -> None:
        self.result += "  external events:\n    "
        for event in element._data:
            event.accept(self)
        self.result += "\n"

    def visit_device(self, element: Device) -> None:
        self.result = "\n"
        if len(element.uses) > 0:
            uses_str = ""
            for device_name in element.uses:
                uses_str += (device_name + ", ")
            self.result += "Device {0} uses {1}:\n".format(element.name, uses_str)
        else:
            self.result += "Device {0}:\n".format(element.name)

        if element.actions.count() > 0:
            element.actions.accept(self)

        if element.internal_events.count() > 0:
            element.internal_events.accept(self)

        if element.external_events.count() > 0:
            element.external_events.accept(self)

        self.result += "  behaviours:\n"
        element.behaviours.accept(self)

        if element.components.count() > 0:
            element.components.accept(self)

        self.result += "  triggers:\n"
        element.triggers.accept(self)

    def __str__(self):
        return self.result
