from __future__ import annotations
from typing import TYPE_CHECKING, Dict
from ast.node import Node
from ast.events import GenericEvent

if TYPE_CHECKING:
    from ast.visitors import Visitor
    from ast.devices import Device


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


class TriggerRuleDeviceNotDeclaredError(Exception):
    pass


class TriggerRuleEventNotDeclaredError(Exception):
    pass
