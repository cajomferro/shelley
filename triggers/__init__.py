from typing import List
from events import GenericEvent, EEvent


class TriggerRule:
    pass


class TriggerRuleEvent(TriggerRule):
    component_name = None  # type: str
    component_event = None  # type: str

    def __init__(self, component_name: str, component_event: str):
        assert (component_name is not None and component_event is not None)
        self.component_name = component_name
        self.component_event = component_event

    def __eq__(self, other):
        if not isinstance(other, TriggerRuleEvent):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of TriggerRule type")

        return self.component_name == other.component_name and self.component_event == other.component_event


class TriggerRuleDouble(TriggerRule):
    left_trigger_rule = None  # type: TriggerRule
    right_trigger_rule = None  # type: TriggerRule

    def __init__(self, left_trigger_rule: TriggerRule, right_trigger_rule: TriggerRule):
        self.left_trigger_rule = left_trigger_rule
        self.right_trigger_rule = right_trigger_rule

    def __eq__(self, other):
        if not isinstance(other, TriggerRuleDouble):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of TriggerRule type")

        return self.left_trigger_rule == other.left_trigger_rule and self.right_trigger_rule == other.right_trigger_rule


class TriggerRuleSequence(TriggerRuleDouble):
    pass


class TriggerRuleChoice(TriggerRuleDouble):
    pass


class TriggerRuleAnd(TriggerRuleDouble):
    pass


class TriggerRuleGroup(TriggerRule):
    trigger_rule = None  # type: TriggerRule

    def __init__(self, trigger_rule: TriggerRule):
        self.trigger_rule = trigger_rule

    def __eq__(self, other):
        if not isinstance(other, TriggerRuleGroup):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of TriggerRule type")

        return self.trigger_rule == other.trigger_rule


class Trigger:
    event = None  # type: EEvent
    trigger_rule = None  # type: TriggerRule

    def __init__(self, event: EEvent, trigger_rule: TriggerRule):
        self.event = event
        self.trigger_rule = trigger_rule

    def __eq__(self, other):
        if not isinstance(other, Trigger):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Trigger type")

        return self.event == other.event  # and self.device_name == other.device_name
