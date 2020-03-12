from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from .node import Node
from .events import GenericEvent
from .components import Component

if TYPE_CHECKING:
    from .visitors import Visitor
    from .devices import Device


class TriggerRule(Node):
    pass


class TriggerRuleFired(TriggerRule):
    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_fired(self)


class TriggerRuleEvent(TriggerRule):
    component = None  # type: Component
    component_event = None  # type: str # TODO: this should be GenericEvent

    def __init__(self, component: Component, component_event: str):
        assert (component.name is not None and component_event is not None)
        self.component = component
        self.component_event = component_event

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_event(self)

    def check_wf_syntax(self, devices: Dict[str, Device], components: Dict[Component, str]) -> None:
        """
        Concrete Components may have special methods that don't exist in their
        base class or interface. The Visitor is still able to use these methods
        since it's aware of the component's concrete class.
        """

        device_name = components[self.component]

        if device_name not in devices:
            raise TriggerRuleDeviceNotDeclaredError(
                "Device type '{0}' has not been declared!".format(self.component.name))

        device = devices[device_name]

        if device is None:
            raise TriggerRuleDeviceNotDeclaredError(
                "Reference for device type '{0}' is None!".format(self.component.name))

        if GenericEvent(self.component_event) not in device.get_all_events():
            raise TriggerRuleEventNotDeclaredError(
                "Event '{0}' not declared for device {1}!".format(self.component_event,
                                                                  self.component.name))

    def __eq__(self, other):
        if not isinstance(other, TriggerRuleEvent):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of TriggerRuleEvent type")

        return self.component.name == other.component.name and self.component_event == other.component_event

    def __str__(self):
        return "{0}.{1}".format(self.component.name, self.component_event)


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


class TriggerRuleDeviceNotDeclaredError(Exception):
    pass


class TriggerRuleEventNotDeclaredError(Exception):
    pass
