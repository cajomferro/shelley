from typing import List, Dict, Set, Tuple
from actions import Action
from events import GenericEvent, IEvent, EEvent
from behaviours import Behaviour
from components import Component
from triggers import Trigger, TriggerRule, TriggerRuleEvent, TriggerRuleGroup, TriggerRuleDouble, TriggerRuleChoice, \
    TriggerRuleSequence, TriggerRuleAnd


class Device:
    name = None  # type: str
    actions = None  # type: List[Action]
    internal_events = None  # type: List[IEvent]
    external_events = None  # type: List[EEvent]
    behaviours = None  # type: List[Behaviour]
    uses = None  # type: List[str]
    components = None  # type: List[Component]
    triggers = None  # type: List[Trigger]

    def __init__(self, name: str,
                 actions: List[Action],
                 internal_events: List[IEvent],
                 external_events: List[EEvent],
                 behaviours: List[Behaviour],
                 uses: List[str] = None,
                 components=None,  # type: List[Component] (cyclic)
                 triggers: List[Trigger] = None):
        assert (name is not None and len(name) > 0), "Device must have a name"

        self.name = name
        self.actions = actions
        self.internal_events = internal_events
        self.external_events = external_events
        self.behaviours = behaviours
        self.uses = uses
        self.components = components
        self.triggers = triggers

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

    def get_all_events(self) -> List[GenericEvent]:
        return self.internal_events + self.external_events

    @staticmethod
    def behaviours_as_event_tuple(behaviours: List[Behaviour]):
        return [(behaviour.e1, behaviour.e2) for behaviour in behaviours]

    @staticmethod
    def components_as_dict(components_list: List[Component]):
        components_dict = {}
        for component in components_list:
            components_dict[component.name] = component.device
        return components_dict

    @staticmethod
    def triggers_as_dict(triggers_list: List[Trigger]) -> Dict[GenericEvent, TriggerRule]:
        triggers_dict = {}
        for trigger in triggers_list:
            triggers_dict[trigger.event] = trigger.trigger_rule
        return triggers_dict

def get_devices_as_set(trigger_rule: TriggerRule,
                       declared_components: Dict[str, Device]) -> List[Set]:
    """
    Represent all traces as a list of sets (without duplicates)
    """
    if isinstance(trigger_rule, TriggerRuleEvent):
        return [{trigger_rule.component_name}]

    elif isinstance(trigger_rule, TriggerRuleGroup):
        return get_devices_as_set(trigger_rule.trigger_rule, declared_components)

    elif isinstance(trigger_rule, TriggerRuleAnd):
        left_set = get_devices_as_set(trigger_rule.left_trigger_rule, declared_components)
        right_set = get_devices_as_set(trigger_rule.right_trigger_rule, declared_components)
        new_list = []

        for elem1 in left_set:
            for elem2 in right_set:
                new_list.append(elem1.union(elem2))

        for elem1 in right_set:
            for elem2 in left_set:
                new_list.append(elem1.union(elem2))

        return new_list

    elif isinstance(trigger_rule, TriggerRuleSequence):
        left = get_devices_as_set(trigger_rule.left_trigger_rule, declared_components)
        right = get_devices_as_set(trigger_rule.right_trigger_rule, declared_components)

        new_list = []

        for elem1 in left:
            for elem2 in right:
                new_list.append(elem1.union(elem2))

        # Alternative
        # for sub_list in left:
        #     for sub_list2 in right:
        #         for sub_list3 in sub_list2:
        #             sub_list.append(sub_list3)
        # return left

        return new_list

    elif isinstance(trigger_rule, TriggerRuleChoice):
        left = get_devices_as_set(trigger_rule.left_trigger_rule, declared_components)
        right = get_devices_as_set(trigger_rule.right_trigger_rule, declared_components)

        result = []
        for elem in left:
            result.append(elem)
        for elem in right:
            result.append(elem)
        return result


def get_devices_as_list(trigger_rule: TriggerRule,
                        declared_components: Dict[str, Device]) -> List[List]:
    """
    Represent all traces as a list of lists (with duplicates)
    """
    if isinstance(trigger_rule, TriggerRuleEvent):
        return [[trigger_rule.component_name]]

    elif isinstance(trigger_rule, TriggerRuleGroup):
        return get_devices_as_list(trigger_rule.trigger_rule, declared_components)

    elif isinstance(trigger_rule, TriggerRuleAnd):
        left = get_devices_as_list(trigger_rule.left_trigger_rule, declared_components)
        right = get_devices_as_list(trigger_rule.right_trigger_rule, declared_components)

        new_list = []
        for elem1 in left:
            for elem2 in right:
                new_list.append(elem1 + elem2)

        for elem1 in right:
            for elem2 in left:
                new_list.append(elem1 + elem2)

        return new_list

    elif isinstance(trigger_rule, TriggerRuleSequence):
        left = get_devices_as_list(trigger_rule.left_trigger_rule, declared_components)
        right = get_devices_as_list(trigger_rule.right_trigger_rule, declared_components)

        new_list = []
        for elem1 in left:
            for elem2 in right:
                new_list.append(elem1 + elem2)

        return new_list

    elif isinstance(trigger_rule, TriggerRuleChoice):
        left = get_devices_as_list(trigger_rule.left_trigger_rule, declared_components)
        right = get_devices_as_list(trigger_rule.right_trigger_rule, declared_components)

        result = []
        for elem in left:
            result.append(elem)
        for elem in right:
            result.append(elem)
        return result
