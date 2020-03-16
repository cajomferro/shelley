from __future__ import annotations
from typing import Dict

from . import Visitor
from shelley.ast.devices import Device
from shelley.ast.actions import Action
from shelley.ast.events import EEvent, IEvent
from shelley.ast.behaviours import Behaviour
from shelley.ast.components import Component
from shelley.ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, TriggerRuleFired


class PrettyPrintVisitor(Visitor):
    declared_devices = None  # type: Dict[str, Device]
    components = None  # type: Dict[Component, str]
    result = None

    def __init__(self, components: Dict[Component, str] = None, declared_devices: Dict[str, Device] = None):
        self.components = components
        self.declared_devices = declared_devices
        self.result = ""

    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        self.result += "fired"

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        self.result += "{0}.{1} ".format(element.component, element.event)

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

    def visit_component(self, element: Component) -> None:
        device_name = self.components[element]
        device = self.declared_devices[device_name]
        self.result += "{0} {1}, ".format(device.name, element.name)

    def visit_behaviour(self, element: Behaviour) -> None:
        if element.action is not None:
            self.result += "    {0} -> {1}() {2}\n".format(element.e1, element.action.name, element.e2)
        else:
            self.result += "    {0} -> {1}\n".format(element.e1, element.e2)

    def visit_action(self, element: Action) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_ievent(self, element: IEvent) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_eevent(self, element: EEvent) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_device(self, element: Device) -> None:
        self.result = "\n"
        if element.uses is not None:
            uses_str = ""
            for device_name in element.uses:
                uses_str += (device_name + ", ")
            self.result += "Device {0} uses {1}:\n".format(element.name, uses_str)
        else:
            self.result += "Device {0}:\n".format(element.name)

        if len(element.actions) > 0:
            self.result += "  actions:\n    ".format(element.name)
            for action in element.actions:
                action.accept(self)
            self.result += "\n"

        if element.internal_events is not None and len(element.internal_events) > 0:
            self.result += "  internal events:\n    ".format(element.name)
            for event in element.internal_events:
                event.accept(self)
            self.result += "\n"

        if element.external_events is not None and len(element.external_events) > 0:
            self.result += "  external events:\n    ".format(element.name)
            for event in element.external_events:
                event.accept(self)
            self.result += "\n"

        self.result += "  behaviours:\n".format(element.name)
        for behaviour in sorted(element.behaviours):
            behaviour.accept(self)

        if element.components is not None:
            self.result += "  components:\n    ".format(element.name)
            for component in element.components:
                component.accept(self)
            self.result += "\n"

        self.result += "  triggers:\n".format(element.name)

        for trigger_event in element.triggers:
            self.result += "    {0}: ".format(trigger_event)
            element.triggers[trigger_event].accept(self)
            self.result += "\n"
        self.result += "\n"

    def __str__(self):
        return self.result
