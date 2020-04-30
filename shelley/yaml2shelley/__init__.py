import yaml
from typing import List, Mapping
import copy
import pathlib
from shelley.yaml2shelley.util import MySafeLoader
from shelley.ast.events import EEvent, EEvents, IEvents
from shelley.ast.actions import Actions
from shelley.ast.behaviors import Behaviors, BehaviorsListDuplicatedError
from shelley.ast.devices import Device
from shelley.ast.components import Components
from shelley.ast.triggers import Triggers
from shelley.ast.rules import (
    TriggerRule,
    TriggerRuleEvent,
    TriggerRuleChoice,
    TriggerRuleSequence,
    TriggerRuleFired,
)


class ShelleyParserError(Exception):
    pass


# def parse_events(input: List[str]) -> EEvents:
#     events: EEvents = EEvents()
#     for event_name in input:
#         events.add(EEvent(event_name))
#     return events

# def parse_behavior_with_events(input: List[List[str]], events: EEvents) -> Behaviors:
#     """
#     Old version that assumes that events must be declared previously
#     :param input:
#     :param events:
#     :return:
#     """
#     behaviors: Behaviors = Behaviors()
#     for beh_transition in input:
#         left = beh_transition[0]
#         right = beh_transition[1]
#         e1 = events.find_by_name(left)
#         e2 = events.find_by_name(right)
#         behaviors.create(e1, e2)
#     return behaviors


def _parse_behavior(
    src: List[List[str]], events: EEvents, behaviors: Behaviors
) -> None:
    """
    Parse behavior by creating discovered events and creating the corresponding transitions
    :param src: behavior input to be parsed, example: [['pressed', 'released'], ['released', 'pressed']]
    :param events: empty collection to store events
    :param behaviors: empty collection to store behavior transitions
    """
    for beh_transition in src:
        left = beh_transition[0]
        try:
            right = beh_transition[1]
        except IndexError:
            raise ShelleyParserError(
                "Missing behaviour right side: [{0}, ???]".format(left)
            )
        e1 = events.find_by_name(left)
        if e1 is None:
            e1 = events.create(left)
        e2 = events.find_by_name(right)
        if e2 is None:
            e2 = events.create(right)
        try:
            behaviors.create(e1, e2)
        except BehaviorsListDuplicatedError as err:
            raise ShelleyParserError("Duplicated behavior '{0}'".format(err))


def _parse_components(src: Mapping[str, str], components: Components) -> None:
    """

    :param src: Example: {'ledA': 'Led', 'ledB': 'Led', 'b': 'Button', 't': 'Timer'},
    :param components:
    :return:
    """
    for component_name in src:
        device_name = src[component_name]
        components.create(component_name, device_name)


def _parse_triggers(
    src: Mapping, events: EEvents, components: Components, triggers: Triggers
) -> None:
    for trigger_event_name in src:
        trigger_rule = _parse_trigger_rule(src[trigger_event_name], components)

        event = events.find_by_name(trigger_event_name)
        if event is None:
            raise ShelleyParserError(
                "Trigger event '{0}' has not been declared".format(trigger_event_name)
            )
        triggers.create(event, trigger_rule)

    for event_name in events.list_str():
        if triggers.find_by_event(event_name) is None:
            raise ShelleyParserError(
                "Missing trigger for event '{0}'".format(event_name)
            )


def _parse_trigger_rule(src, components: Components) -> TriggerRule:
    if isinstance(src, str):
        try:
            c_name, e_name = src.split(".")
        except ValueError as err:
            raise ShelleyParserError("Invalid trigger rule '{0}'. Missing component?".format(src))
        component = components.find_by_name(c_name)
        assert component is not None
        return TriggerRuleEvent(component, EEvent(e_name))
    elif isinstance(src, list) and len(src) == 0:
        raise ShelleyParserError("Trigger must not be empty!")
    elif isinstance(src, list) and len(src) == 1:
        return _parse_trigger_rule(src.pop(0), components)
    elif isinstance(src, list):
        left = _parse_trigger_rule(src.pop(0), components)
        right = _parse_trigger_rule(src, components)
        return TriggerRuleSequence(left, right)
    elif isinstance(src, dict):
        if "xor" in src:
            xor_options: List = src["xor"]
            left_option = xor_options[0]
            right_option = xor_options[1]
            if isinstance(left_option, dict) and "left" in left_option:
                left = _parse_trigger_rule(left_option["left"], components)
                right = _parse_trigger_rule(right_option["right"], components)
                return TriggerRuleChoice(left, right)
            else:
                left = _parse_trigger_rule(left_option, components)
                right = _parse_trigger_rule(right_option, components)
                return TriggerRuleChoice(left, right)
        else:
            raise ShelleyParserError("Unknown option for trigger: ", src)
    else:
        raise ShelleyParserError("Unknown option for trigger: ", src)


# def parse_tests(tests: Mapping):
#     try:
#         testsok = tests['ok']
#     except KeyError:
#         testsok = dict()
#
#     try:
#         testsfail = tests['fail']
#     except KeyError:
#         testsfail = dict()
#
#     for tname in testsok:
#


def _create_device_from_yaml(yaml_code) -> Device:
    try:
        device_name = yaml_code["device"]["name"]
    except KeyError:
        raise ShelleyParserError("Device must have a name")

    # try:
    #     device_events = yaml_code['device']['events']
    # except KeyError:
    #     raise Exception("Device must have events")

    try:
        device_start_events = yaml_code["device"]["start_events"]
    except KeyError:
        raise ShelleyParserError("Please specify at least one start event")

    try:
        device_behavior = yaml_code["device"]["behavior"]
    except KeyError:
        raise ShelleyParserError("Device must have a behavior")

    try:
        device_components = yaml_code["device"]["components"]
    except KeyError:
        device_components = dict()

    try:
        device_triggers = yaml_code["device"]["triggers"]
    except KeyError:
        device_triggers = dict()

    try:
        test_macro = yaml_code["test_macro"]
    except KeyError:
        test_macro = {"ok": dict(), "fail": dict()}

    try:
        test_macro["ok"]
    except KeyError:
        raise ShelleyParserError("Missing key 'ok' for test macro!")

    try:
        test_macro["fail"]
    except KeyError:
        raise ShelleyParserError("Missing key 'fail' for test macro!")

    try:
        test_micro = yaml_code["test_micro"]
    except KeyError:
        test_micro = {"ok": dict(), "fail": dict()}

    try:
        test_micro["ok"]
    except KeyError:
        raise ShelleyParserError("Missing key 'ok' for test micro!")

    try:
        test_micro["fail"]
    except KeyError:
        raise ShelleyParserError("Missing key 'fail' for test micro!")

    events: EEvents = EEvents()
    behaviors: Behaviors = Behaviors()
    components: Components = Components()
    triggers: Triggers = Triggers()
    _parse_behavior(device_behavior, events, behaviors)
    _parse_components(device_components, components)

    if (
        len(device_triggers) == 0 and len(device_components) == 0
    ):  # auto-create triggers for simple devices
        for event in events.list():
            triggers.create(event, TriggerRuleFired())
    elif len(device_triggers) == 0 and len(device_components) > 0:
        raise ShelleyParserError("Device with components must also have triggers!")
    else:
        _parse_triggers(
            copy.deepcopy(device_triggers), events, components, triggers
        )  # deep copy because i will consume some list elements (not really important)

    # if len(tests) > 0:
    #     parse_tests(tests)

    device = Device(
        device_name,
        Actions(),
        IEvents(),
        events,
        device_start_events,
        behaviors,
        triggers,
        components=components,
    )

    device.test_macro = test_macro
    device.test_micro = test_micro

    return device


def get_shelley_from_yaml(path: pathlib.Path) -> Device:
    with path.open(mode="r") as stream:
        yaml_code = yaml.load(stream, MySafeLoader)
    return _create_device_from_yaml(yaml_code)
