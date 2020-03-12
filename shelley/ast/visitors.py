from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Set

from .devices import Device
from .actions import Action
from .events import GenericEvent, EEvent, IEvent
from .behaviours import Behaviour
from .components import Component
from .rules import TriggerRule, TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent


class Visitor(ABC):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """

    @abstractmethod
    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        pass

    @abstractmethod
    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        pass

    @abstractmethod
    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        pass

    @abstractmethod
    def visit_component(self, element: Component) -> None:
        pass

    @abstractmethod
    def visit_behaviour(self, element: Behaviour) -> None:
        pass

    @abstractmethod
    def visit_action(self, element: Action) -> None:
        pass

    @abstractmethod
    def visit_ievent(self, element: IEvent) -> None:
        pass

    @abstractmethod
    def visit_eevent(self, element: EEvent) -> None:
        pass

    @abstractmethod
    def visit_device(self, element: Device) -> None:
        pass


class CheckWFSyntaxVisitor(Visitor):
    device = None  # type: Device
    declared_devices = None  # type: Dict[str, Device]

    def __init__(self, device: Device, declared_devices: Dict[str, Device]):
        self.device = device
        self.declared_devices = declared_devices

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
        for t in element.triggers:
            t.accept(self)


class PrettyPrintVisitor(Visitor):
    result = None

    def __init__(self):
        self.result = ""

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        self.result += "{0}.{1} ".format(element.component_name, element.component_event)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        self.result += "("
        element.left_trigger_rule.accept(self)
        self.result += " ; "
        element.right_trigger_rule.accept(self)
        self.result += ")"

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        self.result += "("
        element.left_trigger_rule.accept(self)
        self.result += " xor "
        element.right_trigger_rule.accept(self)
        self.result += ")"

    def visit_component(self, element: Component) -> None:
        self.result += "{0} {1}, ".format(element.device.name, element.name)

    def visit_behaviour(self, element: Behaviour) -> None:
        self.result += "    {0} -> {1}\n".format(element.e1, element.e2)

    def visit_action(self, element: Action) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_ievent(self, element: IEvent) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_eevent(self, element: EEvent) -> None:
        self.result += "{0}, ".format(element.name)

    def visit_device(self, element: Device) -> None:
        uses_str = ""
        for device_name in element.uses:
            uses_str += (device_name + ", ")
        self.result += "Device {0} uses {1}:\n".format(element.name, uses_str)
        if len(element.actions) > 0:
            self.result += "actions:\n    ".format(element.name)
            for action in element.actions:
                action.accept(self)
            self.result += "\n"
        self.result += "  events:\n    ".format(element.name)
        for event in element.get_all_events():
            event.accept(self)
        self.result += "\n"
        self.result += "  behaviours:\n".format(element.name)
        for behaviour in element.behaviours:
            behaviour.accept(self)
        self.result += "  components:\n    ".format(element.name)
        for component in element.components:
            component.accept(self)
        self.result += "\n"
        self.result += "  triggers:\n".format(element.name)
        for trigger in element.triggers:
            trigger.accept(self)
        self.result += "\n"

    def __str__(self):
        return self.result
