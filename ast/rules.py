from __future__ import annotations
from abc import abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devices import Device

from typing import Dict
from events import GenericEvent
from ast.triggers import TriggersVisitor

from ast.node import Visitor, Node


class TriggerRule(Node):
    pass


class TriggerRuleEvent(TriggerRule):
    component_name = None  # type: str
    component_event = None  # type: str

    def __init__(self, component_name: str, component_event: str):
        assert (component_name is not None and component_event is not None)
        self.component_name = component_name
        self.component_event = component_event

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_event(self)

    def check_wf_syntax(self, declared_components: Dict[str, Device]) -> None:
        """
        Concrete Components may have special methods that don't exist in their
        base class or interface. The Visitor is still able to use these methods
        since it's aware of the component's concrete class.
        """

        try:
            component_device = declared_components[self.component_name]
        except KeyError as error:
            raise TriggerRuleDeviceNotDeclaredError(
                "Device type '{0}' has not been declared!".format(self.component_name))

        if component_device is None:
            raise TriggerRuleDeviceNotDeclaredError(
                "Reference for device type '{0}' is None!".format(self.component_name))

        # TODO: I had to create a dummy generic event here because I cannot compare strings with events
        if GenericEvent(self.component_event) not in component_device.get_all_events():
            raise TriggerRuleEventNotDeclaredError(
                "Event '{0}' not declared for device {1}!".format(self.component_event,
                                                                  self.component_name))

    def __eq__(self, other):
        if not isinstance(other, TriggerRuleEvent):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of TriggerRuleEvent type")

        return self.component_name == other.component_name and self.component_event == other.component_event


class TriggerRuleSequence(TriggerRule):
    def __init__(self, left_trigger_rule: TriggerRule, right_trigger_rule: TriggerRule):
        self.left_trigger_rule = left_trigger_rule
        self.right_trigger_rule = right_trigger_rule

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_sequence(self)

    def __eq__(self, other):
        if not isinstance(other, TriggerRuleSequence):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of TriggerRuleSequence type")

        return self.left_trigger_rule == other.left_trigger_rule and self.right_trigger_rule == other.right_trigger_rule


class TriggerRuleChoice(TriggerRule):
    def __init__(self, left_trigger_rule: TriggerRule, right_trigger_rule: TriggerRule):
        self.left_trigger_rule = left_trigger_rule
        self.right_trigger_rule = right_trigger_rule

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_choice(self)

    def __eq__(self, other):
        if not isinstance(other, TriggerRuleChoice):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of TriggerRuleChoice type")

        return self.left_trigger_rule == other.left_trigger_rule and self.right_trigger_rule == other.right_trigger_rule


class RulesVisitor(Visitor):
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


class CheckWFSyntax(RulesVisitor):
    declared_components = None

    def __init__(self, declared_components: Dict[str, Device]):
        self.declared_components = declared_components

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        element.check_wf_syntax(self.declared_components)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        element.left_trigger_rule.accept(self)
        element.right_trigger_rule.accept(self)


class PrettyPrint(TriggersVisitor):
    rules = None

    def __init__(self):
        self.rules = ""

    def visit_trigger_rule_event(self, element: TriggerRuleEvent) -> None:
        self.rules += "{0}.{1} ".format(element.component_name, element.component_event)

    def visit_trigger_rule_sequence(self, element: TriggerRuleSequence) -> None:
        self.rules += "("
        element.left_trigger_rule.accept(self)
        self.rules += " ; "
        element.right_trigger_rule.accept(self)
        self.rules += ")"

    def visit_trigger_rule_choice(self, element: TriggerRuleChoice) -> None:
        self.rules += "("
        element.left_trigger_rule.accept(self)
        self.rules += " xor "
        element.right_trigger_rule.accept(self)
        self.rules += ")"


class TriggerRuleDeviceNotDeclaredError(Exception):
    pass


class TriggerRuleEventNotDeclaredError(Exception):
    pass
