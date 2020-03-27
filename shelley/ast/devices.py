from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING

from .node import Node
from .actions import Action, Actions
from .behaviors import Behavior, Behaviors
from .components import Component, Components
from .triggers import Trigger, Triggers
from .rules import TriggerRule
from .events import GenericEvent, IEvent, EEvent, IEvents, EEvents, Events

if TYPE_CHECKING:
    from .visitors import Visitor


def discover_uses(components: Components) -> List[str]:
    uses = list()
    for component_name in components.components_to_devices:
        device_name = components.components_to_devices[component_name]
        if device_name not in uses:
            uses.append(device_name)
    return uses


class Device(Node):
    """
    \\hard{D} -> categoria sintática
    """
    name: str = None
    actions: Actions = None
    internal_events: IEvents = None
    external_events: EEvents = None
    start_events: List[str] = None
    behaviors = None  # type: Behaviors
    uses = None  # type: List[str]
    components = None  # type: Components
    triggers = None  # type: Triggers

    def __init__(self, name: str,
                 actions: Actions,
                 internal_events: IEvents,
                 external_events: EEvents,
                 start_events: List[str],
                 behaviors: Behaviors,
                 triggers: Triggers,
                 uses: List[str] = list(),
                 components=Components()):

        self.name = name
        self.actions = actions
        self.internal_events = internal_events
        self.external_events = external_events
        self.start_events = start_events
        self.behaviors = behaviors
        self.uses = uses
        self.components = components
        self.triggers = triggers

        # find used devices from components if not specified
        if len(self.uses) == 0 and len(self.components.components_to_devices) != 0:
            self.uses = discover_uses(self.components)

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_device(self)

    def check_is_duplicated(self, devices: List[Device]):
        if self in devices:
            raise DevicesListDuplicatedError(
                "Duplicated device with name '{0}'".format(self.name))

    # def find_event(self, event_name: str):
    #     result = [event for event in self.get_all_events() if event.name == event_name]
    #     if len(result) == 0:
    #         raise Exception("Event not found!")
    #     return result[0]
    #
    # def find_trigger(self, event_name: str) -> Trigger:
    #     result = [trigger for trigger in self.triggers if trigger.event.name == event_name]
    #     if len(result) == 0:
    #         raise Exception("Trigger for event '{0}' not found!".format(event_name))
    #     return result[0]
    #
    # def find_behaviour(self, left_event_name: str, right_event_name: str) -> Behaviour:
    #     result = [behaviour for behaviour in self.behaviours if
    #               behaviour.e1.name == left_event_name and behaviour.e2.name == right_event_name]
    #     if len(result) == 0:
    #         raise Exception("Behaviour not found!")
    #     return result[0]
    #
    def get_all_events(self) -> Events:
        return self.external_events.merge(self.internal_events)

    #
    # @staticmethod
    # def behaviours_as_event_tuple(behaviours: Set[Behaviour]):
    #     return [(behaviour.e1, behaviour.e2) for behaviour in behaviours]
    #
    # @staticmethod
    # def triggers_as_dict(triggers_list: Set[Trigger]) -> Dict[GenericEvent, TriggerRule]:
    #     triggers_dict = {}
    #     for trigger in triggers_list:
    #         triggers_dict[trigger.event] = trigger.trigger_rule
    #     return triggers_dict

    def __eq__(self, other):
        if not isinstance(other, Device):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Device type")

        return self.name == other.name


class DevicesListDuplicatedError(Exception):
    pass
