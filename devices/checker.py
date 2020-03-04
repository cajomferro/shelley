from typing import List, Dict, Set, Tuple
from devices import Device
from actions.checker import check as check_actions
from events.checker import check as check_events
from behaviours.checker import check as check_behaviours
from components.checker import check as check_components
from triggers.checker import check as check_triggers
from events import GenericEvent, IEvent, EEvent
from behaviours import Behaviour
from components import Component
from triggers import Trigger, TriggerRule, TriggerRuleEvent, TriggerRuleGroup, TriggerRuleDouble, TriggerRuleChoice, \
    TriggerRuleSequence


class DeviceCompositionInvalidIntersection(Exception):
    pass


class DeviceInvalidTriggerRuleReduction(Exception):
    pass


def check(device: Device, declared_devices: Dict[str, Device], is_composite=False) -> bool:
    if len(device.actions) > 0:
        check_actions(device.actions)

    declared_i_events, declared_e_events = check_events(device.get_all_events())  # type: List[IEvent], List[EEvent]

    behaviours_result = []  # type: List[Behaviour]
    check_behaviours(device.behaviours, device.actions, declared_i_events, declared_e_events, behaviours_result)

    if is_composite:
        declared_components = check_components(device.components, device.uses,
                                               declared_devices)  # type: Dict[str, Device]

        triggers_result = []  # type: List[Trigger]
        check_triggers(device.triggers, declared_e_events, declared_components, triggers_result)

        check_composition(device)


def check_composition(device: Device) -> bool:
    for behaviour in device.behaviours:
        t_e1 = device.find_trigger(behaviour.e1.name)
        t_e2 = device.find_trigger(behaviour.e2.name)
        case_intersection = get_devices_from_trigger_rule(t_e1.trigger_rule).intersection(
            get_devices_from_trigger_rule(t_e2.trigger_rule))
        case_e2_not_e1 = get_devices_from_trigger_rule(t_e1.trigger_rule).difference(
            get_devices_from_trigger_rule(t_e2.trigger_rule))
        case_e1_not_e2 = get_devices_from_trigger_rule(t_e2.trigger_rule).difference(
            get_devices_from_trigger_rule(t_e1.trigger_rule))

        for component in device.components:
            if component.name in case_intersection:
                _check_intersection(component, t_e1, t_e2, device.behaviours)
            elif component.name in case_e2_not_e1:
                _check_e2_not_e1(device, behaviour, component, t_e2)
            else:
                _check_e1_not_e2(device, behaviour, component, t_e1)


def _check_intersection(component: Component, t_e1: Trigger, t_e2: Trigger, behaviours: List[Behaviour]):
    behaviours_dict = Device.behaviours_as_event_tuple(component.device.behaviours)
    trigger_rules_e1 = get_rules_by_device(component.name, t_e1.trigger_rule)
    trigger_rules_e2 = get_rules_by_device(component.name, t_e2.trigger_rule)
    is_valid_rule(component.name, trigger_rules_e1, trigger_rules_e2, behaviours_dict)


#        raise DeviceCompositionInvalidIntersection(
#            "Invalid intersection for '{0}' and '{1}'".format(t_e1.event.name, t_e2.event.name))


def _check_e2_not_e1(device: Device, behaviour: Behaviour, component: Component, t_e2: Trigger):
    behaviours_dict = Device.behaviours_as_event_tuple(component.device.behaviours)
    triggers_dict = Device.triggers_as_dict(device.triggers)
    for e in pred(behaviour.e1, component.device, behaviours_dict, triggers_dict):
        t_e = device.find_trigger(e.name)
        trigger_rules_e = get_rules_by_device(component.name, t_e.trigger_rule)
        trigger_rules_e2 = get_rules_by_device(component.name, t_e2.trigger_rule)
        is_valid_rule(component.name, trigger_rules_e, trigger_rules_e2,
                      Device.behaviours_as_event_tuple(device.behaviours))


def _check_e1_not_e2(device: Device, behaviour: Behaviour, component: Component, t_e1: Trigger):
    behaviours_dict = Device.behaviours_as_event_tuple(component.device.behaviours)
    triggers_dict = Device.triggers_as_dict(device.triggers)
    for e in succ(behaviour.e2, component.device, behaviours_dict, triggers_dict):
        t_e = device.find_trigger(e.name)
        trigger_rules_e1 = get_rules_by_device(component.name, t_e1.trigger_rule)
        trigger_rules_e = get_rules_by_device(component.name, t_e.trigger_rule)
        is_valid_rule(component.name, trigger_rules_e1, trigger_rules_e,
                      Device.behaviours_as_event_tuple(device.behaviours))


def get_devices_from_trigger_rule(trigger_rule: TriggerRule) -> Set[str]:
    """
    The set of components (component names) in a trigger rule (Fig. 10)

    Collect all devices used in a trigger (i.e., in all trigger rules)
    :param trigger_rule: the root of the tree representing all trigger rules
    :return: a set with devices (without duplicates)
    """
    if isinstance(trigger_rule, TriggerRuleEvent):
        return {trigger_rule.component_name}

    elif isinstance(trigger_rule, TriggerRuleGroup):
        return get_devices_from_trigger_rule(trigger_rule.trigger_rule)

    elif isinstance(trigger_rule, TriggerRuleDouble):  # Sequence, Choice, And
        left = get_devices_from_trigger_rule(trigger_rule.left_trigger_rule)
        right = get_devices_from_trigger_rule(trigger_rule.right_trigger_rule)
        return left.union(right)


def get_rules_by_device(device_name: str,
                        trigger_rule: TriggerRule) -> TriggerRule:
    """
    Restriction of a trigger rule to a device (Fig. 11)

    Collect all rules that use device with "device_name"
    :param device_name: name of the device
    :param trigger_rule: the root of the tree representing all trigger rules (with all devices)
    :return: tree of trigger rules
    """
    if isinstance(trigger_rule, TriggerRuleEvent):
        return TriggerRuleEvent(device_name, trigger_rule.component_event)

    elif isinstance(trigger_rule, TriggerRuleGroup):
        return get_rules_by_device(device_name, trigger_rule.trigger_rule)

    elif isinstance(trigger_rule, TriggerRuleSequence):
        current_rule = None
        r1 = None
        r2 = None
        if device_name in get_devices_from_trigger_rule(trigger_rule.left_trigger_rule):
            r1 = get_rules_by_device(device_name, trigger_rule.left_trigger_rule)
        if device_name in get_devices_from_trigger_rule(trigger_rule.right_trigger_rule):
            r2 = get_rules_by_device(device_name, trigger_rule.right_trigger_rule)
        if r1 is not None and r2 is not None:
            current_rule = TriggerRuleSequence(r1, r2)
        elif r1 is None and r2 is not None:
            current_rule = r2
        elif r1 is not None and r2 is None:
            current_rule = r1
        return current_rule

    elif isinstance(trigger_rule, TriggerRuleChoice):
        current_rule = None
        r1 = None
        r2 = None
        if device_name in get_devices_from_trigger_rule(trigger_rule.left_trigger_rule):
            r1 = get_rules_by_device(device_name, trigger_rule.left_trigger_rule)
        if device_name in get_devices_from_trigger_rule(trigger_rule.right_trigger_rule):
            r2 = get_rules_by_device(device_name, trigger_rule.right_trigger_rule)
        if r1 is not None and r2 is not None:
            current_rule = TriggerRuleChoice(r1, r2)
        elif r1 is None and r2 is not None:
            current_rule = r2
        elif r1 is not None and r2 is None:
            current_rule = r1
        return current_rule


def is_valid_rule(device_name: str, trigger_rule_left: TriggerRule,
                  trigger_rule_right: TriggerRule,
                  behaviours: List[Tuple[GenericEvent, GenericEvent]]) -> None:
    """
    Valid reduction for trigger rules (Fig. 12)

    Given two rules, check if they are part of the behaviour
    :param trigger_rule_left:
    :param trigger_rule_right:
    :param behaviours:
    :return:
    """
    if isinstance(trigger_rule_left, TriggerRuleEvent) and isinstance(trigger_rule_right, TriggerRuleEvent):
        # print([(behaviour[0].name, behaviour[1].name) for behaviour in behaviours])
        if not (GenericEvent(trigger_rule_left.component_event),
                GenericEvent(trigger_rule_right.component_event)) in behaviours:
            raise DeviceInvalidTriggerRuleReduction(
                "Invalid behaviour: {0}.{1} -> {0}.{2}".format(device_name, trigger_rule_left.component_event,
                                                               trigger_rule_right.component_event))

    if isinstance(trigger_rule_left, TriggerRuleSequence):
        r1 = trigger_rule_left.left_trigger_rule
        r2 = trigger_rule_left.right_trigger_rule
        r3 = trigger_rule_right
        r1_r2_is_valid = is_valid_rule(device_name, r1, r2, behaviours)
        r2_r3_is_valid = is_valid_rule(device_name, r2, r3, behaviours)

    if isinstance(trigger_rule_right, TriggerRuleSequence):
        r1 = trigger_rule_left
        r2 = trigger_rule_right.left_trigger_rule
        r3 = trigger_rule_right.right_trigger_rule
        r1_r2_is_valid = is_valid_rule(device_name, r1, r2, behaviours)
        r2_r3_is_valid = is_valid_rule(device_name, r2, r3, behaviours)

    if isinstance(trigger_rule_left, TriggerRuleChoice):
        r1 = trigger_rule_left.left_trigger_rule
        r2 = trigger_rule_left.right_trigger_rule
        r3 = trigger_rule_right
        r1_r2_is_valid = is_valid_rule(device_name, r1, r3, behaviours)
        r2_r3_is_valid = is_valid_rule(device_name, r2, r3, behaviours)

    if isinstance(trigger_rule_right, TriggerRuleChoice):
        r1 = trigger_rule_left
        r2 = trigger_rule_right.left_trigger_rule
        r3 = trigger_rule_right.right_trigger_rule
        r1_r2_is_valid = is_valid_rule(device_name, r1, r2, behaviours)
        r2_r3_is_valid = is_valid_rule(device_name, r1, r3, behaviours)


def pred(event: GenericEvent, component_device: Device,
         behaviours: List[Tuple[GenericEvent, GenericEvent]],
         triggers: Dict[GenericEvent, TriggerRule]) -> Set[GenericEvent]:
    """
    Predecessor for a composite device given one of its components
    Collects the first previous event in the composite device where a component is used

    ep (paper notation) = event_left

    :param event: composite device event
    :param component_device: component device in the composite device
    :param behaviours: list of behaviours of the composite device
    :param triggers: dict of triggers of the composite device
    :return: set with composite device events that happen before event
    """
    if len(behaviours) == 0:
        return set()

    # behaviours (b1) becomes b2 (b1 with one tuple less)
    event_left, event_right = behaviours.pop(0)  # type: GenericEvent, GenericEvent

    if event_right != event:  # e1 != e
        return pred(event, component_device, behaviours, triggers)
    else:
        if component_device in get_devices_from_trigger_rule(triggers[event_left]):
            return {event_left}.union(pred(event, component_device, behaviours, triggers))
        else:
            return pred(event_left, component_device, behaviours, triggers).union(
                pred(event, component_device, behaviours, triggers))


def succ(event: GenericEvent, component_device: Device,
         behaviours: List[Tuple[GenericEvent, GenericEvent]],
         triggers: Dict[GenericEvent, TriggerRule]) -> Set[GenericEvent]:
    """
    Successor for a composite device given one of its components
    Collects the first following event in the composite device where a component is used

    e_1/e (paper notation) = event_left
    e_s (paper notation) = event_right

    :param event: composite device event
    :param component_device: component device in the composite device
    :param behaviours: list of behaviours of the composite device
    :param triggers: dict of triggers of the composite device
    :return: set with composite device events that happen before event
    """
    if len(behaviours) == 0:
        return set()

    # behaviours (b1) becomes b2 (b1 with one tuple less)
    event_left, event_right = behaviours.pop(0)  # type: GenericEvent, GenericEvent

    if event_left != event:  # e1 != e
        return succ(event, component_device, behaviours, triggers)
    else:
        if component_device in get_devices_from_trigger_rule(triggers[event_right]):
            return {event_right}.union(succ(event, component_device, behaviours, triggers))
        else:
            return succ(event_right, component_device, behaviours, triggers).union(
                succ(event, component_device, behaviours, triggers))
