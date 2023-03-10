from __future__ import annotations
from abc import abstractmethod
from typing import TYPE_CHECKING, Dict, List
from dataclasses import dataclass, field

from shelley.ast.node import Node
from shelley.ast.components import Component, Components

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor
    from shelley.ast.devices import Device


class TriggerRuleDeviceNotDeclaredError(Exception):
    pass


class TriggerRuleEventNotDeclaredError(Exception):
    pass


class TriggerRuleNotNoneError(Exception):
    pass


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

        return visitor.visit_trigger_rule_fired(self)

    def __str__(self):
        return "fired"


@dataclass(order=True)
class TriggerRuleEvent(TriggerRule):
    component: Component
    event: str

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        return visitor.visit_trigger_rule_event(self)

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

        # TODO: maybe this code could be simpler
        try:
            device.events[self.event]
        except KeyError:
            raise TriggerRuleEventNotDeclaredError(
                "Event '{0}' not declared for device {1}!".format(
                    self.event, self.component.name
                )
            )

    def __str__(self):
        return "{0}.{1}".format(self.component.name, self.event)


@dataclass(order=True)
class TriggerRuleSequence(TriggerRule):
    left_trigger_rule: TriggerRule
    right_trigger_rule: TriggerRule

    def __post_init__(self):
        if self.left_trigger_rule is None:
            raise TriggerRuleNotNoneError(
                "TriggerRuleSequence left rule cannot be None!"
            )
        if self.right_trigger_rule is None:
            raise TriggerRuleNotNoneError(
                "TriggerRuleSequence left rule cannot be None!"
            )

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        return visitor.visit_trigger_rule_sequence(self)

    def __str__(self):
        return f"{self.left_trigger_rule}; {self.right_trigger_rule}"


@dataclass(order=True)
class TriggerRuleChoice(TriggerRule):
    choices: List[TriggerRule] = field(default_factory=list)

    def __post_init__(self):
        for rule in self.choices:
            if rule is None:
                raise TriggerRuleNotNoneError("TriggerRuleChoice rule cannot be None!")

    def add_choice(self, choice: TriggerRule):
        if choice not in self.choices:
            self.choices.append(choice)

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        return visitor.visit_trigger_rule_choice(self)

    def __str__(self):
        choices_str = [str(choice) for choice in self.choices]
        final_str = ""
        for choice_str in choices_str:
            final_str += f" {{{choice_str}}} +"
        final_str = final_str[:-2]
        return str(final_str)


@dataclass(order=True)
class TriggerRuleLoop(TriggerRule):
    loop: TriggerRule

    def __post_init__(self):
        if self.loop is None:
            raise TriggerRuleNotNoneError("TriggerRuleLoop rule cannot be None!")

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        return visitor.visit_trigger_rule_loop(self)
