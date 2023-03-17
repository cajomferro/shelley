import copy
import logging
from typing import Mapping, List
from shelley.ast.devices import Device as ShelleyDevice
from shelley.ast.behaviors import Behaviors, BehaviorsListDuplicatedError, Behavior
from shelley.ast.events import Event, Events
from shelley.ast.triggers import Triggers, Trigger
from shelley.ast.rules import TriggerRuleChoice, TriggerRuleFired

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyshelley")


def optimize(device: ShelleyDevice):
    group_by_e1: Mapping[str, List[str]] = elements_that_share_e1(device.behaviors)

    shared_e2: Mapping[str, List[str]] = elements_that_share_e2(group_by_e1)

    to_be_merged = elements_to_be_merged(device, group_by_e1, shared_e2)

    update_behaviors(device, to_be_merged)

    update_triggers(device.triggers, to_be_merged)

    update_events(device.events, to_be_merged)


def update_behaviors(device: ShelleyDevice, to_be_merged: Mapping[str, List[str]]):
    logger.debug("Updating behaviors...")
    behaviors = device.behaviors
    logger.debug(f"Before: {behaviors.list_str()}")
    merged_behaviors = Behaviors()

    if len(to_be_merged.keys()):
        for op_name, extra_ops in to_be_merged.items():
            for b in behaviors:
                e2_name = b.e2.name if b.e2 else ""
                b_copy = copy.deepcopy(b)
                if b_copy.e1.name not in extra_ops:
                    if e2_name in extra_ops:
                        b_copy.e2 = device.events.find_by_name(op_name)
                    try:
                        merged_behaviors.add(b_copy)
                    except BehaviorsListDuplicatedError:
                        pass
        device.behaviors = merged_behaviors

    logger.debug(f"After: {device.behaviors.list_str()}")


def update_triggers(triggers: Triggers, to_be_merged):
    logger.debug("Updating triggers...")
    logger.debug(f"Before: {triggers}")
    for op_name, extra_ops in to_be_merged.items():
        left_rule = triggers.get_rule(op_name)
        for extra_op_name in extra_ops:
            right_rule = triggers.get_rule(extra_op_name)
            choice = TriggerRuleChoice()
            choice.choices.extend([left_rule, right_rule])
            left_rule = choice
        logger.debug(left_rule)
        triggers.update_rule(op_name, left_rule)
    logger.debug(f"After: {triggers}")


def update_events(events: Events, to_be_merged):
    logger.debug("Updating events...")
    logger.debug(f"Before: {events.list_str()}")
    for op_name, extra_ops in to_be_merged.items():
        for extra_op in extra_ops:
            if events.remove_by_name(extra_op) is None:
                logger.debug("Warning! Operation not removed: ", extra_op)
    logger.debug(f"After: {events.list_str()}")


def elements_to_be_merged(
    device: ShelleyDevice,
    shared_e1: Mapping[str, List[str]],
    shared_e2: Mapping[str, List[str]],
):
    """ """
    result = dict()
    for key_e2, value_e2 in shared_e2.items():
        for e1, e1_list in shared_e1.items():
            if all(elem in e1_list for elem in value_e2):
                if isinstance(
                    device.triggers.get_rule(e1), TriggerRuleFired
                ):  # only care for empty body operations
                    result[value_e2[0]] = value_e2[1:]
    logger.debug(f"Elements to be merged: {result}")
    return result


def elements_that_share_e1(behaviors: Behaviors):
    """
    input: ['try_open_1 -> close', 'try_open_2 -> fail', 'try_open_3 -> fail', 'try_open -> try_open_1', 'try_open -> try_open_2', 'try_open -> try_open_3', 'fail -> ', 'close -> try_open']
    output: {'try_open_1': ['close'], 'try_open_2': ['fail'], 'try_open_3': ['fail'], 'try_open': ['try_open_1', 'try_open_2', 'try_open_3'], 'fail': [''], 'close': ['try_open']}
    """
    result = {}
    for b in behaviors:
        if not b.e1.name in result.keys():
            e2_name = b.e2.name if b.e2 else ""
            result[b.e1.name] = [e2_name]
        else:
            result[b.e1.name] = result[b.e1.name] + [b.e2.name]
    logger.debug(f"Group by e1: {result}")
    return result


def elements_that_share_e2(
    share_e1: Mapping[str, List[str]]
) -> Mapping[str, List[str]]:
    """
    input: {'try_open_1': ['close'], 'try_open_2': ['fail'], 'try_open_3': ['fail'], 'try_open': ['try_open_1', 'try_open_2', 'try_open_3'], 'fail': ['try_open'], 'close': ['try_open']}
    output: {'fail': ['try_open_2', 'try_open_3'], 'try_open': ['fail', 'close']}
    """
    e2_dict = {}
    for e1, e2_list in share_e1.items():
        if len(e2_list) == 1:
            if not e2_list[0] in e2_dict.keys():
                e2_dict[e2_list[0]] = [e1]
            else:
                e2_dict[e2_list[0]] = e2_dict[e2_list[0]] + [e1]

    result = {}
    for key, value in e2_dict.items():
        if (
            len(value) > 1
        ):  # here we only care operations that might have something to share (len(e2 operations) > 1)
            result[key] = value

    logger.debug(f"Shared e2: {result}")
    return result
