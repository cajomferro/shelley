import yaml
from typing import List, Mapping, Dict
import copy
import pathlib
from shelley.yaml2shelley.util import MySafeLoader
from shelley.ast.events import Event, Events
from shelley.ast.behaviors import Behaviors, BehaviorsListDuplicatedError
from shelley.ast.devices import Device
from shelley.ast.components import Components
from shelley.ast.triggers import Triggers, TriggersListDuplicatedError
from shelley.ast.rules import (
    TriggerRule,
    TriggerRuleEvent,
    TriggerRuleChoice,
    TriggerRuleSequence,
    TriggerRuleFired,
)


class ShelleyParserError(Exception):
    pass


def _parse_behavior(
    src: List[List[str]], events: Events, behaviors: Behaviors, triggers: Triggers
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

        # TODO: do we want to force user to declare all events? right now I am creating if not declared
        # and device has no components. To autocreate events from behaviors when there is components,
        # it is required to have the notion of a empty trigger rule

        try:
            e1 = events[left]
        except KeyError as err:
            e1 = events.create(left)
            triggers.create(e1, TriggerRuleFired())
            # raise ShelleyParserError(
            #     "Behavior uses undeclared event '{0}'".format(left)
            # )

        try:
            e2 = events[right]
        except KeyError as err:
            e2 = events.create(right)
            triggers.create(e2, TriggerRuleFired())
            # raise ShelleyParserError(
            #     "Behavior uses undeclared event '{0}'".format(right)
            # )

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
    src: Mapping, events: Events, components: Components, triggers: Triggers
) -> None:
    """

    :param src: events section from yaml as dict
    :param events: empty list of events to store discovered events
    :param components:
    :param triggers:
    :return:
    """

    assert len(events) == 0
    assert len(triggers) == 0

    #   # there are defined components but no triggers
    #   raise ShelleyParserError("Device with components must also have triggers!")

    # there are no events declared, they will be auto discovered on behavior
    if len(src) == 0:
        return

    src_events = copy.deepcopy(src)
    if not isinstance(src_events, list):
        raise ShelleyParserError(
            "Invalid syntax for events. Expecting list but found {0}: {1}".format(
                type(src_events), src_events
            )
        )

    for src_event in src_events:
        if isinstance(src_event, str):
            events.create(src_event)
        elif isinstance(src_event, dict):
            try:
                event_name = list(src_event)[0]
                event_data = src_event[event_name]
            except:
                raise ShelleyParserError("Invalid syntax for event '{0}'", src_event)

            is_start: bool = False
            is_final: bool = True
            micro: Dict = {}

            try:
                is_start = event_data["start"]
            except KeyError:
                pass
            except TypeError:
                raise ShelleyParserError(
                    "Type error for event {0}, field {1}. Bad indentation?".format(
                        event_name, "start"
                    )
                )

            try:
                is_final = event_data["final"]
            except KeyError:
                pass
            except TypeError:
                raise ShelleyParserError(
                    "Type error for event {0}, field {1}. Bad indentation?".format(
                        event_name, "final"
                    )
                )

            try:
                micro = event_data["micro"]
            except KeyError:
                pass

            if len(micro) > 0 and len(components) == 0:
                raise ShelleyParserError(
                    "Event '{0}' specifies micro behavior but device has no components!".format(
                        event_name
                    )
                )

            event: Event = events.create(event_name, is_start, is_final)

            if len(micro) > 0:

                trigger_rule = _parse_trigger_rule(micro, components)
                triggers.create(event, trigger_rule)
            else:
                pass  # TODO: what happens in this case?!

                # HOW SHALL WE DEAL WITH EVENTS THAT HAVE EMPTY MICRO (WHEN OTHERS DON'T)?
                # for event_name in events.list_str():
                #     if triggers.find_by_event(event_name) is None:
                #         raise ShelleyParserError(
                #             "Missing trigger for event '{0}'".format(event_name)
                #         )
        else:
            raise ShelleyParserError(
                "Invalid syntax for event. Expecting string or dict but found {0}".format(
                    src_event
                )
            )

    # auto-create triggers
    #if len(components) == 0:
    for event in events.list():
        try:
            triggers.create(event, TriggerRuleFired())
        except TriggersListDuplicatedError:
            pass


def _parse_trigger_rule(src, components: Components) -> TriggerRule:
    if isinstance(src, str):
        try:
            c_name, e_name = src.split(".")
        except ValueError as err:
            raise ShelleyParserError(
                "Invalid trigger rule '{0}'. Missing component?".format(src)
            )
        component = components[c_name]
        assert component is not None
        return TriggerRuleEvent(component, e_name)
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


def _create_device_from_yaml(yaml_code: Dict) -> Device:
    try:
        device_name = yaml_code["device"]["name"]
    except KeyError:
        raise ShelleyParserError("Device must have a name")

    try:
        device_behavior = yaml_code["device"]["behavior"]
    except KeyError:
        raise ShelleyParserError("Device must have a behavior")

    try:
        device_components = yaml_code["device"]["components"]
    except KeyError:
        device_components = dict()

    try:
        device_triggers = yaml_code["device"]["events"]
    except KeyError:
        device_triggers = dict()
        # raise ShelleyParserError("Device must have events")

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

    events: Events = Events()
    behaviors: Behaviors = Behaviors()
    components: Components = Components()
    triggers: Triggers = Triggers()
    _parse_components(device_components, components)
    _parse_triggers(copy.deepcopy(device_triggers), events, components, triggers)
    _found_events_count: int = len(events)
    _parse_behavior(device_behavior, events, behaviors, triggers)

    # TODO: not required if we create empty micro for auto discovered event in behaviors
    # if len(components) > 0 and len(events) != _found_events_count:
    #     raise ShelleyParserError(
    #         "Device with components must explicitly declare all events"
    #     )

    # if not specified, first event is the start event
    if len(events.start_events()) == 0:
        first_event = events.list()[0]
        first_event.is_start = True

    device = Device(device_name, events, behaviors, triggers, components=components,)

    device.test_macro = test_macro
    device.test_micro = test_micro

    return device


def get_shelley_from_yaml(path: pathlib.Path) -> Device:
    with path.open(mode="r") as stream:
        yaml_code = yaml.load(stream, MySafeLoader)
    return _create_device_from_yaml(yaml_code)
