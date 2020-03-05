from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from ast.devices import Device
    from wfsyntax.ast.triggers import Trigger
    from ast.actions import Action
    from ast.events import EEvent, IEvent
    from ast.behaviours import Behaviour
    from ast.components import Component
    from ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent


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
    def visit_trigger(self, element: Trigger) -> None:
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
    actions = None  # type: List[Action]
    ievents = None  # type: List[IEvent]
    eevents = None  # type: List[EEvent]
    behaviours = None  # type: List[Behaviour]
    components = None  # type: List[Component]
    triggers = None  # type: List[Trigger]
    declared_devices = None  # type: Dict[str, Device]
    declared_uses = None  # type: List[str]

    def __init__(self, declared_uses: List[str], declared_devices: Dict[str, Device]):
        self.actions = []
        self.ievents = []
        self.eevents = []
        self.triggers = []
        self.declared_devices = declared_devices
        self.declared_uses = declared_uses

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        element.check_wf_syntax(self.declared_devices)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_trigger(self, element: Trigger) -> None:
        element.check(self.eevents, self.triggers)
        element.trigger_rule.accept(self)

    def visit_component(self, element: Component) -> None:
        element.check(self.declared_uses, self.declared_devices, self.components)

    def visit_behaviour(self, element: Behaviour) -> None:
        element.check(self.actions, self.ievents + self.eevents, self.behaviours)

    def visit_action(self, element: Action) -> None:
        element.check(self.actions)

    def visit_ievent(self, element: IEvent) -> None:
        element.check(self.ievents)

    def visit_eevent(self, element: EEvent) -> None:
        element.check(self.eevents)

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

    def visit_trigger(self, element: Trigger) -> None:
        self.result += "    {0} <- ".format(element.event.name)
        element.trigger_rule.accept(self)
        self.result += "\n"

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
