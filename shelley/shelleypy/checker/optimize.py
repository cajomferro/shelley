import copy
import logging
from typing import Mapping, List
import shelley.ast.triggers
from shelley.shelleypy.checker.checker import PyVisitor
from shelley.shelleypy.checker.checker import extract_node
from shelley.ast.visitors.shelley2lark import Shelley2Lark
from shelley.ast.devices import Device as ShelleyDevice
from shelley.ast.behaviors import Behaviors, BehaviorsListDuplicatedError, Behavior
from shelley.ast.events import Event, Events
from shelley.ast.triggers import Triggers, Trigger
from shelley.ast.rules import TriggerRuleChoice

from shelley.parsers.shelley_lark_parser import parser as lark_parser, ShelleyLanguage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyshelley")

def optimize(device: ShelleyDevice):
    shared_e1 = elements_that_share_e1(device.behaviors)
    logger.debug(shared_e1)

    shared_e2: Mapping[str, List[str]] = elements_that_share_e2(device.behaviors)
    logger.debug(shared_e2)

    to_be_merged = elements_to_be_merged(shared_e1, shared_e2)
    logger.debug(to_be_merged)

    update_behaviors(device, to_be_merged)
    logger.debug(device.behaviors.list_str())

    update_triggers(device.triggers, to_be_merged)

    update_events(device.events, to_be_merged)
    logger.debug(device.events.list_str())

def update_behaviors(device: ShelleyDevice, to_be_merged):
    logger.debug("Updating behaviors...")
    behaviors = device.behaviors
    logger.debug("Before: ", behaviors.list_str())
    merged_behaviors = Behaviors()
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
    logger.debug("After: ", behaviors.list_str())

def update_triggers(triggers: Triggers, to_be_merged):
    logger.debug("Updating triggers...")
    logger.debug("Before: ", triggers)
    for op_name, extra_ops in to_be_merged.items():
        left_rule = triggers.get_rule(op_name)
        for extra_op_name in extra_ops:
            right_rule = triggers.get_rule(extra_op_name)
            choice = TriggerRuleChoice()
            choice.choices.extend([left_rule, right_rule])
            left_rule = choice
        logger.debug(left_rule)
        triggers.update_rule(op_name, left_rule)
    logger.debug("After: ", triggers)


def update_events(events: Events, to_be_merged):
    logger.debug("Updating events...")
    logger.debug("Before: ", events.list_str())
    for op_name, extra_ops in to_be_merged.items():
        for extra_op in extra_ops:
            if events.remove_by_name(extra_op) is None:
                logger.debug("Warning! Operation not removed: ", extra_op)
    #     left_rule = triggers.get_rule(op_name)
    #     for extra_op_name in extra_ops:
    #         right_rule = triggers.get_rule(extra_op_name)
    #         choice = TriggerRuleChoice()
    #         choice.choices.extend([left_rule, right_rule])
    #         left_rule = choice
    #     logger.debug(left_rule)
    #     triggers.update_rule(op_name, left_rule)
    logger.debug("After: ", events.list_str())


def elements_to_be_merged(shared_e1: Mapping[str, List[str]], shared_e2: Mapping[str, List[str]]):
    """

    """
    to_be_merged = dict()
    for key_e2, value_e2 in shared_e2.items():
        for key_e1, value_e1 in shared_e1.items():
            if all(elem in value_e1  for elem in value_e2):
                to_be_merged[value_e2[0]] = value_e2[1:]
    return to_be_merged

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

    return result

def elements_that_share_e2(behaviors: Behaviors):
    """
    input: ['try_open_1 -> close', 'try_open_2 -> fail', 'try_open_3 -> fail', 'try_open -> try_open_1', 'try_open -> try_open_2', 'try_open -> try_open_3', 'fail -> ', 'close -> try_open']
    output: {'fail': ['try_open_2', 'try_open_3']}
    """
    e2_dict = {}
    for b in behaviors:
        if b.e2 and len(b.e2.name):
            if not b.e2.name in e2_dict.keys():
                e2_dict[b.e2.name] = [b.e1.name]
            else:
                e2_dict[b.e2.name] = e2_dict[b.e2.name] + [b.e1.name]

    e2_dict_final = {}
    for key, value in e2_dict.items():
        if len(value) > 1:
            e2_dict_final[key] = value
    return e2_dict_final