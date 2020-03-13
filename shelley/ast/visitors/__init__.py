from __future__ import annotations
from abc import ABC, abstractmethod

from shelley.ast.devices import Device
from shelley.ast.actions import Action
from shelley.ast.events import EEvent, IEvent
from shelley.ast.behaviours import Behaviour
from shelley.ast.components import Component
from shelley.ast.rules import TriggerRuleSequence, TriggerRuleChoice, TriggerRuleEvent, TriggerRuleFired


class Visitor(ABC):
    """
    The Visitor Interface declares a set of visiting methods that correspond to
    component classes. The signature of a visiting method allows the visitor to
    identify the exact class of the component that it's dealing with.
    """

    @abstractmethod
    def visit_trigger_rule_fired(self, element: TriggerRuleFired) -> None:
        pass

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
