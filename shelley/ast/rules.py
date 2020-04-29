from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING, Dict
from dataclasses import dataclass

from .node import Node
from .events import GenericEvent
from .components import Component, Components

if TYPE_CHECKING:
    from .visitors import Visitor
    from .devices import Device


class TriggerRule(Node):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass


class TriggerRuleFired(TriggerRule):
    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_fired(self)


@dataclass(order=True)
class TriggerRuleEvent(TriggerRule):
    component: Component
    event: GenericEvent

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_event(self)

    def check_wf_syntax(
        self, devices: Dict[str, Device], components: Components
    ) -> None:
        """
        Concrete Components may have special methods that don't exist in their
        base class or interface. The Visitor is still able to use these methods
        since it's aware of the component's concrete class.
        """

        device_name = components.get_device_name(self.component.name)

        if device_name not in devices:
            raise TriggerRuleDeviceNotDeclaredError(
                "Device type '{0}' has not been declared!".format(self.component.name)
            )

        device = devices[device_name]

        if device is None:
            raise TriggerRuleDeviceNotDeclaredError(
                "Reference for device type '{0}' is None!".format(self.component.name)
            )

        if self.event not in device.get_all_events()._data:
            raise TriggerRuleEventNotDeclaredError(
                "Event '{0}' not declared for device {1}!".format(
                    self.event.name, self.component.name
                )
            )

    # def __init__(self, component: Component, event: GenericEvent):
    #     assert (component.name is not None and event is not None)
    #     self.component = component
    #     self.event = event
    #
    # def __eq__(self, other):
    #     if not isinstance(other, TriggerRuleEvent):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance is not of TriggerRuleEvent type")
    #
    #     return self.component.name == other.component.name and self.event.name == other.event.name
    #

    def __str__(self):
        return "{0}.{1}".format(self.component.name, self.event.name)


@dataclass(order=True)
class TriggerRuleSequence(TriggerRule):
    left_trigger_rule: TriggerRule
    right_trigger_rule: TriggerRule

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_sequence(self)

    # def __init__(self, left_trigger_rule: TriggerRule, right_trigger_rule: TriggerRule):
    #     self.left_trigger_rule = left_trigger_rule
    #     self.right_trigger_rule = right_trigger_rule
    #
    # def __eq__(self, other):
    #     if not isinstance(other, TriggerRuleSequence):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance is not of TriggerRuleSequence type")
    #
    #     return self.left_trigger_rule == other.left_trigger_rule and self.right_trigger_rule == other.right_trigger_rule


@dataclass(order=True)
class TriggerRuleChoice(TriggerRule):
    left_trigger_rule: TriggerRule
    right_trigger_rule: TriggerRule

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_trigger_rule_choice(self)

    # def __init__(self, left_trigger_rule: TriggerRule, right_trigger_rule: TriggerRule):
    #     self.left_trigger_rule = left_trigger_rule
    #     self.right_trigger_rule = right_trigger_rule
    #
    # def __eq__(self, other):
    #     if not isinstance(other, TriggerRuleChoice):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance is not of TriggerRuleChoice type")
    #
    #     return self.left_trigger_rule == other.left_trigger_rule and self.right_trigger_rule == other.right_trigger_rule
    #


class TriggerRuleDeviceNotDeclaredError(Exception):
    pass


class TriggerRuleEventNotDeclaredError(Exception):
    pass
