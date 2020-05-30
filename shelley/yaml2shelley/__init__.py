import yaml
from typing import List, Mapping, Dict, Optional, Union, Set
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
        src: List[List[str]],
        events: Events,
        behaviors: Behaviors,
        components: Components,
        triggers: Triggers,
) -> None:
    """
    Parse behavior by creating discovered events and creating the corresponding transitions
    :param src: behavior input to be parsed, example: [['pressed', 'released'], ['released', 'pressed']]
    :param events: empty collection to store events
    :param behaviors: empty collection to store behavior transitions
    """

    discovered_events: Set[str] = set()

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
            e1 = _parse_event(left, events, components, triggers)
            # raise ShelleyParserError(
            #     "Behavior uses undeclared event '{0}'".format(left)
            # )

        try:
            e2 = events[right]
        except KeyError as err:
            e2 = _parse_event(right, events, components, triggers)
            # raise ShelleyParserError(
            #     "Behavior uses undeclared event '{0}'".format(right)
            # )

        discovered_events.add(e1.name)
        discovered_events.add(e2.name)

        try:
            behaviors.create(e1, e2)
        except BehaviorsListDuplicatedError as err:
            raise ShelleyParserError("Duplicated behavior '{0}'".format(err))

    difference = set(events.list_str()).difference(discovered_events)
    if len(difference) > 0:
        raise ShelleyParserError(
            f"invalid operations {difference!r}. Operations must be referred in the behavior."
        )


def _parse_components(src: Mapping[str, str], components: Components) -> None:
    """

    :param src: Example: {'ledA': 'Led', 'ledB': 'Led', 'b': 'Button', 't': 'Timer'},
    :param components:
    :return:
    """
    for component_name in src:
        device_name = src[component_name]
        components.create(component_name, device_name)


def _parse_event(
        src: Union[str, dict], events: Events, components: Components, triggers: Triggers
) -> Event:
    event: Optional[Event] = None

    if isinstance(src, str):
        event = events.create(src)
        _parse_triggers(None, event, components, triggers)
    elif isinstance(src, dict):
        try:
            event_name = list(src)[0]
            event_data = src[event_name]
        except:
            raise ShelleyParserError("Invalid syntax for event '{0}'", src)

        is_start: bool = False
        is_final: bool = True
        micro: Optional[Dict] = None

        try:
            is_start = event_data["start"]
            assert type(is_start) == bool
        except KeyError:
            pass
        except TypeError:
            raise ShelleyParserError(
                "Type error for event {0}, field {1}. Bad indentation?".format(
                    event_name, "start"
                )
            )
        except AssertionError:
            raise ShelleyParserError(
                "Type error for event {0}, field {1}. Expecting bool, found {2}!".format(
                    event_name, "start", type(event_data["start"])
                )
            )

        try:
            is_final = event_data["final"]
            assert type(is_final) == bool
        except KeyError:
            pass
        except TypeError:
            raise ShelleyParserError(
                "Type error for event {0}, field {1}. Bad indentation?".format(
                    event_name, "final"
                )
            )
        except AssertionError:
            raise ShelleyParserError(
                "Type error for event {0}, field {1}. Expecting bool, found {2}!".format(
                    event_name, "final", type(event_data["final"])
                )
            )

        try:
            micro = event_data["micro"]
        except KeyError:
            pass

        event = events.create(event_name, is_start, is_final)

        _parse_triggers(micro, event, components, triggers)

    else:
        raise ShelleyParserError(
            "Invalid syntax for event. Expecting string or dict but found {0}".format(
                src
            )
        )
    assert event is not None

    return event


def _parse_events(
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
        _parse_event(src_event, events, components, triggers)


def _parse_triggers(
        src: Optional[Dict], event: Event, components: Components, triggers: Triggers
) -> None:
    """

    :param src: dict value corresponding to key 'micro'
    :param event:
    :param components:
    :param triggers:
    :return:
    """
    trigger_rule: Optional[TriggerRule] = None

    if (
            src is not None and len(components) == 0
    ):  # simple device with micro (not allowed!)
        raise ShelleyParserError(
            f"invalid integration of operation '{event.name}'. Remove integration (system has 0 components)."
        )
    elif (
            src is None and len(components) > 0
    ):  # composition device not declaring micro for this event (not allowed!)
        count = len(components)
        raise ShelleyParserError(
            f"missing integration of operation '{event.name}'. Specify integration (system has {count} components)."
        )
    elif src is None and len(components) == 0:  # simple device without micro (ok!)
        trigger_rule = TriggerRuleFired()
    elif (
            src is not None and len(components) > 0
    ):  # composition device declaring trigger for this event (ok!)
        trigger_rule = _parse_trigger_rule(src, components)
    else:
        raise ShelleyParserError("unknown option for operation: ", src)

    assert trigger_rule is not None
    triggers.create(event, trigger_rule)


def _parse_trigger_rule(src, components: Components) -> TriggerRule:
    if src is None:
        raise ShelleyParserError("Micro must not be empty!")

    if isinstance(src, str):
        try:
            c_name, e_name = src.split(".")
        except ValueError as err:
            raise ShelleyParserError(
                "Invalid micro rule '{0}'. Missing component?".format(src)
            )
        component = components[c_name]
        assert component is not None
        return TriggerRuleEvent(component, e_name)
    elif isinstance(src, list) and len(src) == 0:
        raise ShelleyParserError("Micro must not be empty!")
    elif isinstance(src, list) and len(src) == 1:
        return _parse_trigger_rule(src.pop(0), components)
    elif isinstance(src, list):
        left = _parse_trigger_rule(src.pop(0), components)
        right = _parse_trigger_rule(src, components)
        return TriggerRuleSequence(left, right)
    elif isinstance(src, dict) and len(src) == 0:
        raise ShelleyParserError("Micro must not be empty!")
    elif isinstance(src, dict):
        if "xor" in src:
            trule_choice = TriggerRuleChoice()
            if src['xor'] is None:
                raise ShelleyParserError("xor must have at least one option!")
            for option in src["xor"]:
                trule_choice.choices.append(_parse_trigger_rule(option, components))
            return trule_choice
        elif "seq" in src:
            if src['seq'] is None:
                raise ShelleyParserError("seq must have at least one option!")
            left = _parse_trigger_rule(src['seq'].pop(0), components)
            if len(src['seq']) > 0:
                right = _parse_trigger_rule(src['seq'], components)
                return TriggerRuleSequence(left, right)
            else:
                return left
        else:
            raise ShelleyParserError("Unknown option for micro: ", src)
    else:
        raise ShelleyParserError("Unknown option for micro: ", src)


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
        device_events = yaml_code["device"]["events"]
    except KeyError:
        device_events = dict()
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
    _parse_events(copy.deepcopy(device_events), events, components, triggers)
    _found_events_count: int = len(events)
    _parse_behavior(device_behavior, events, behaviors, components, triggers)

    # TODO: not required if we create empty micro for auto discovered event in behaviors
    # if len(components) > 0 and len(events) != _found_events_count:
    #     raise ShelleyParserError(
    #         "Device with components must explicitly declare all events"
    #     )

    # if not specified, first event is the start event
    if len(events.start_events()) == 0:
        first_event = events.list()[0]
        first_event.is_start = True

    # we do not allow triggers without at least one trigger rule
    for event in events.list():
        assert triggers.get_rule(event.name) is not None

    # at this point, this must be true
    assert len(events) == len(triggers)

    device = Device(device_name, events, behaviors, triggers, components=components, )

    device.test_macro = test_macro
    device.test_micro = test_micro

    return device


def get_shelley_from_yaml(path: pathlib.Path) -> Device:
    with path.open(mode="r") as stream:
        yaml_code = yaml.load(stream, MySafeLoader)
    return _create_device_from_yaml(yaml_code)


def get_shelley_from_yaml_str(yaml_str: str) -> Device:
    return _create_device_from_yaml(yaml.load(yaml_str, MySafeLoader))
