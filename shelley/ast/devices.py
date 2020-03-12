from __future__ import annotations
from typing import Dict, Set, TYPE_CHECKING

from .node import Node
from .actions import Action
from .behaviours import Behaviour
from .components import Component
from .triggers import Trigger
from .rules import TriggerRule
from .events import GenericEvent, IEvent, EEvent

if TYPE_CHECKING:
    from .visitors import Visitor


class Device(Node):
    """
    \\hard{D} -> categoria sintática
    """
    name = None  # type: str
    actions = None  # type: Set[Action]
    internal_events = None  # type: Set[IEvent]
    external_events = None  # type: Set[EEvent]
    behaviours = None  # type: Set[Behaviour]
    uses = None  # type: Set[str]
    components = None  # type: Dict[Component, str]
    triggers = None  # type: Dict[GenericEvent, TriggerRule]

    def __init__(self, name: str,
                 actions: Set[Action],
                 internal_events: Set[IEvent],
                 external_events: Set[EEvent],
                 behaviours: Set[Behaviour],
                 triggers: Dict[GenericEvent, TriggerRule],
                 uses: Set[str] = None,
                 components: Dict[Component, str] = None):

        self.name = name
        self.actions = actions
        self.internal_events = internal_events
        self.external_events = external_events
        self.behaviours = behaviours
        self.uses = uses
        self.components = components
        self.triggers = triggers

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_device(self)

    def check_is_duplicated(self, devices: Set[Device]):
        if self in devices:
            raise DevicesListDuplicatedError(
                "Duplicated device with name '{0}'".format(self.name))

    def find_event(self, event_name: str):
        result = [event for event in self.get_all_events() if event.name == event_name]
        if len(result) == 0:
            raise Exception("Event not found!")
        return result[0]

    def find_trigger(self, event_name: str) -> Trigger:
        result = [trigger for trigger in self.triggers if trigger.event.name == event_name]
        if len(result) == 0:
            raise Exception("Trigger for event '{0}' not found!".format(event_name))
        return result[0]

    def find_behaviour(self, left_event_name: str, right_event_name: str) -> Behaviour:
        result = [behaviour for behaviour in self.behaviours if
                  behaviour.e1.name == left_event_name and behaviour.e2.name == right_event_name]
        if len(result) == 0:
            raise Exception("Behaviour not found!")
        return result[0]

    def get_all_events(self) -> Set[GenericEvent]:
        return self.internal_events.union(self.external_events)

    @staticmethod
    def behaviours_as_event_tuple(behaviours: Set[Behaviour]):
        return [(behaviour.e1, behaviour.e2) for behaviour in behaviours]

    @staticmethod
    def triggers_as_dict(triggers_list: Set[Trigger]) -> Dict[GenericEvent, TriggerRule]:
        triggers_dict = {}
        for trigger in triggers_list:
            triggers_dict[trigger.event] = trigger.trigger_rule
        return triggers_dict

    def __eq__(self, other):
        if not isinstance(other, Device):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Device type")

        return self.name == other.name


class DevicesListDuplicatedError(Exception):
    pass
