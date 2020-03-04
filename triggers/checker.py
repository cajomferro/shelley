from typing import List, Dict

from events import GenericEvent
from events import EEvent
from devices import Device
from triggers import Trigger, TriggerRule, TriggerRuleEvent, TriggerRuleGroup


class TriggersListEmptyError(Exception):
    pass


class TriggersListDuplicatedError(Exception):
    pass


class TriggersEventUndeclaredError(Exception):
    pass


class TriggerRulesListEmptyError(Exception):
    pass


class TriggerRuleDeviceNotDeclaredError(Exception):
    pass


class TriggerRuleEventNotDeclaredError(Exception):
    pass


# TODO: GROUP TRIGGER RULES HAVE EMPTY EVENT, WILL RAISE ERROR
def check_trigger_rules(trigger_rule: TriggerRule,
                        declared_components: Dict[str, Device]):
    if trigger_rule is None:
        raise TriggerRulesListEmptyError("List of trigger rules cannot be empty!")

    if type(trigger_rule) is TriggerRuleEvent:

        try:
            component_device = declared_components[trigger_rule.component_name]
        except KeyError as error:
            raise TriggerRuleDeviceNotDeclaredError(
                "Device type '{0}' has not been declared!".format(trigger_rule.component_name))

        if component_device is None:
            raise TriggerRuleDeviceNotDeclaredError(
                "Reference for device type '{0}' is None!".format(trigger_rule.component_name))

        # TODO: I had to create a dummy generic event here because I cannot compare strings with events
        if GenericEvent(trigger_rule.component_event) not in component_device.get_all_events():
            raise TriggerRuleEventNotDeclaredError(
                "Event '{0}' not declared for device {1}!".format(trigger_rule.component_event,
                                                                  trigger_rule.component_name))

    elif type(trigger_rule) is TriggerRuleGroup:
        check_trigger_rules(trigger_rule.trigger_rule, declared_components)
    else:
        check_trigger_rules(trigger_rule.left_trigger_rule, declared_components)
        check_trigger_rules(trigger_rule.right_trigger_rule, declared_components)


def check(triggers: List[Trigger],
          declared_e_events: List[EEvent],
          declared_components: Dict[str, Device],
          result: List[Trigger]) -> None:
    _check(triggers.copy(), declared_e_events.copy(), declared_components.copy(), result)


def _check(triggers: List[Trigger],
           declared_e_events: List[EEvent],
           declared_components: Dict[str, Device],
           result: List[Trigger]) -> None:
    """
    Check triggers
    :param triggers:
    :param declared_e_events:
    :param declared_components: dict mapping component name to device type (cf. components checker)
    :param result: list of triggers
    :return: void
    """
    if len(triggers) == 0:
        raise TriggersListEmptyError("List of triggers cannot be empty!")

    current_trigger = triggers.pop()  # pop from tail

    if len(triggers) == 0:  # last element to process
        if current_trigger.event not in declared_e_events:
            raise TriggersEventUndeclaredError(
                "Left event '{0}' must be declared in events section!".format(current_trigger.event.name))

        if current_trigger in result:
            raise TriggersListDuplicatedError(
                "Duplicated trigger with event '{0}'".format(current_trigger.event.name))

        check_trigger_rules(current_trigger.trigger_rule, declared_components)

        result.append(current_trigger)

    else:
        _check([current_trigger], declared_e_events, declared_components, result)
        _check(triggers, declared_e_events, declared_components, result)
