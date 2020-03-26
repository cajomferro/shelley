import yaml
from typing import List, Mapping, NoReturn
from shelley.ast.events import EEvent, EEvents, IEvents
from shelley.ast.actions import Actions
from shelley.ast.behaviors import Behaviors
from shelley.ast.devices import Device
from shelley.ast.components import Components
from shelley.ast.triggers import Triggers
from shelley.ast.rules import TriggerRule, TriggerRuleEvent, TriggerRuleChoice, TriggerRuleSequence, TriggerRuleFired
import copy


def parse_events(input: List[str]) -> EEvents:
    events: EEvents = EEvents()
    for event_name in input:
        events.add(EEvent(event_name))
    return events


def parse_behavior(input: List[List[str]], events: EEvents, behaviors: Behaviors) -> NoReturn:
    """
    Parse behavior by creating discovered events and creating the corresponding transitions
    :param input: behavior input to be parsed, example: [['pressed', 'released'], ['released', 'pressed']]
    :param events: empty collection to store events
    :param behaviors: empty collection to store behavior transitions
    """
    for beh_transition in input:
        left = beh_transition[0]
        right = beh_transition[1]
        e1 = events.find_by_name(left)
        if e1 is None:
            e1 = events.create(left)
        e2 = events.find_by_name(right)
        if e2 is None:
            e2 = events.create(right)
        behaviors.create(e1, e2)


def parse_components(input: Mapping[str, str], components: Components) -> NoReturn:
    """

    :param input: Example: {'ledA': 'Led', 'ledB': 'Led', 'b': 'Button', 't': 'Timer'},
    :param components:
    :return:
    """
    for component_name in input:
        device_name = input[component_name]
        components.create(component_name, device_name)


def parse_triggers(input: dict, events: EEvents, components: Components, triggers: Triggers) -> NoReturn:
    for trigger_event_name in input:
        trigger_rule = parse_trigger_rule(input[trigger_event_name], components)

        event = events.find_by_name(trigger_event_name)
        triggers.create(event, trigger_rule)


def parse_trigger_rule(input, components: Components) -> TriggerRule:
    if isinstance(input, str):
        c_name, e_name = input.split(".")
        component = components.find_by_name(c_name)
        return TriggerRuleEvent(component, EEvent(e_name))
    elif isinstance(input, list) and len(input) == 1:
        return parse_trigger_rule(input.pop(0), components)
    elif isinstance(input, list):
        left = parse_trigger_rule(input.pop(0), components)
        right = parse_trigger_rule(input, components)
        return TriggerRuleSequence(left, right)
    elif isinstance(input, dict):
        xor_options: List = input['xor']
        left = parse_trigger_rule(xor_options[0], components)
        right = parse_trigger_rule(xor_options[1], components)
        return TriggerRuleChoice(left, right)


def parse_behavior_with_events(input: List[List[str]], events: EEvents) -> Behaviors:
    """
    Old version that assumes that events must be declared previously
    :param input:
    :param events:
    :return:
    """
    behaviors: Behaviors = Behaviors()
    for beh_transition in input:
        left = beh_transition[0]
        right = beh_transition[1]
        e1 = events.find_by_name(left)
        e2 = events.find_by_name(right)
        behaviors.create(e1, e2)
    return behaviors


def create_device_from_yaml(yaml_code) -> Device:
    try:
        device_name = yaml_code['device']['name']
    except KeyError:
        raise Exception("Device must have a name")

    # try:
    #     device_events = yaml_code['device']['events']
    # except KeyError:
    #     raise Exception("Device must have events")

    try:
        device_behavior = yaml_code['device']['behavior']
    except KeyError:
        raise Exception("Device must have a behavior")

    try:
        device_components = yaml_code['device']['components']
    except KeyError:
        device_components = dict()

    try:
        device_triggers = yaml_code['device']['triggers']
    except KeyError:
        device_triggers = dict()

    events: EEvents = EEvents()
    behaviors: Behaviors = Behaviors()
    components: Components = Components()
    triggers: Triggers = Triggers()
    parse_behavior(device_behavior, events, behaviors)
    parse_components(device_components, components)

    if len(device_triggers) == 0:  # auto-create triggers for simple devices
        for event in events.list():
            triggers.create(event, TriggerRuleFired())
    else:
        parse_triggers(copy.deepcopy(device_triggers), events, components,
                       triggers)  # deep copy because i will consume some list elements (not really important)

    return Device(device_name, Actions(), IEvents(), events, behaviors, triggers, components=components)
