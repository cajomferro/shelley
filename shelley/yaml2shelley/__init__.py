import yaml
from typing import List, Mapping, Dict, Optional, Union, Set, Iterable, Collection, Any
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
    # "invalid operation declaration {event.name!r}: integration section missing. Only declare an integration rule when there are components (system has {count} components). Hint: write integration rule or remove all components."

    def __init__(
        self,
        *,
        title: str,
        reason: Optional[str] = None,
        hints: Collection[str] = (),
        parent: Optional["ShelleyParserError"] = None,
    ) -> None:
        assert (reason is None and parent is not None) or (
            reason is not None and parent is None
        )
        self.title = title
        self.reason = reason
        self.hints = hints
        self.parent = parent

    def get_parents(self) -> Iterable["ShelleyParserError"]:
        err = self.parent
        while err is not None:
            yield err
            err = err.parent

    def get_titles(self) -> Iterable[str]:
        yield self.title
        for err in self.get_parents():
            yield err.title

    def __str__(self) -> str:
        if self.parent is None:
            hints = (
                "\n" + "\n".join(f"Hint: {x}" for x in self.hints)
                if len(self.hints) > 0
                else ""
            )
            return f"{self.title}: {self.reason}{hints}"
        else:
            return self.title + ": " + str(self.parent)


def BehaviorError(reason: Optional[str] = None, hints=(), parent=None):
    return ShelleyParserError(
        title="behavior error", reason=reason, hints=hints, parent=parent
    )


class OperationDeclError(ShelleyParserError):
    def __init__(
        self,
        names=Optional[Iterable[str]],
        reason: Optional[str] = None,
        hints: Collection[str] = (),
        parent: Optional[ShelleyParserError] = None,
    ) -> None:
        if names is None:
            title = "operation declaration error"
        else:
            ns = list(names)
            title = f"operation declaration error in {ns!r}"
        super(OperationDeclError, self).__init__(
            title=title, reason=reason, hints=hints, parent=parent
        )


class IntegrationRuleError(ShelleyParserError):
    def __init__(self, reason: str, hints=()):
        super(IntegrationRuleError, self).__init__(
            title="integration rule error", reason=reason, hints=hints
        )


def EmptySequenceError() -> ShelleyParserError:
    return IntegrationRuleError(
        reason="An empty sequence introduces ambiguity.",
        hints=["remove empty sequence or add subsystem call to sequence."],
    )


def SystemDeclError(reason: str):
    return ShelleyParserError(title="system error", reason=reason)


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
        if not isinstance(left, str):
            raise BehaviorError(reason=f"Expecting a string, but got: {left!r}")

        try:
            right = beh_transition[1]
        except IndexError:
            raise BehaviorError(
                reason="Missing behavior right side: [{0}, ???]".format(left)
            )
        if not isinstance(right, str):
            raise BehaviorError(reason=f"Expecting a string, but got: {right!r}")
        # TODO: do we want to force user to declare all events? right now I am creating if not declared
        # and device has no components. To autocreate events from behaviors when there is components,
        # it is required to have the notion of a empty trigger rule

        try:
            e1 = events[left]
        except KeyError:
            raise ShelleyParserError(
                title="invalid transition",
                reason=f"Behavior uses undeclared event {left!r}",
            )

        try:
            e2 = events[right]
        except KeyError:
            raise ShelleyParserError(
                title="invalid transition",
                reason=f"Behavior uses undeclared event {right!r}",
            )

        discovered_events.add(left)
        discovered_events.add(right)
        try:
            e1 = events[left]
            e2 = events[right]
            behaviors.create(e1, e2)
        except BehaviorsListDuplicatedError as err:
            raise BehaviorError(reason=f"duplicated behavior '{err}'")

    difference = set(events.list_str()).difference(discovered_events)
    if len(difference) > 0:
        evt1 = list(sorted(difference))[0]
        raise OperationDeclError(
            names=difference,
            reason="Every operation declaration must be referred in the behavior.",
            hints=[
                f"remove the definition of {evt1!r} or add a transition with {evt1!r} to the behavior section."
            ],
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


def parse_bool_field(
    field_name: str, default_value: bool, event_name: str, event_data: Any
) -> bool:
    try:
        result = event_data[field_name]
        if isinstance(result, bool):
            return result
        else:
            raise OperationDeclError(
                names=[event_name],
                reason=f"Expecting a boolean, but found {type(result).__name__}: {result!r}",
            )
    except KeyError:
        if default_value is None:
            raise OperationDeclError(
                names=[event_name],
                reason=f"Field {field_name!r} is missing",
                hints=["Define boolean field {field_name!r}"],
            )
        else:
            return default_value


def _parse_event_list(data: dict, key: str, events: Events,) -> List[Event]:
    ANY = "$ANY"
    TITLE = f"section {key!r}"
    HINTS = [
        f"To list all operations write '{key}: {ANY}'",
    ]
    try:
        obj = data[key]
    except KeyError:
        raise ShelleyParserError(
            title=TITLE, reason=f"section {key!r} is missing", hints=HINTS,
        )
    if not (isinstance(obj, list) or (isinstance(obj, str) and obj.strip() == ANY)):
        raise ShelleyParserError(
            title=TITLE,
            reason=f"expecting string '{ANY}', or a list of operation names (strings), but got: {obj!r}",
            hints=HINTS,
        )

    if isinstance(obj, str):
        return events.list()
    if isinstance(obj, list):
        result = []
        for elem in obj:
            try:
                result.append(events[elem])
            except KeyError:
                raise ShelleyParserError(
                    title=TITLE,
                    reason=f"unknown operation {elem!r}",
                    hints=HINTS + [f"Declare operation {elem!r}"],
                )
        return result

    raise ValueError("Should not reach here!", obj)


def _parse_event(
    event_name: str,
    event_data: dict,
    events: Events,
    components: Components,
    triggers: Triggers,
) -> Event:
    event: Optional[Event] = None
    unknown_keys = set(event_data.keys()) - {"start", "final", "micro", "next"}
    if len(unknown_keys) > 0:
        raise OperationDeclError(
            names=[event_name], reason=f"remove unexpected keys: {unknown_keys!r}"
        )

    is_start: bool = parse_bool_field("start", False, event_name, event_data)
    is_final: bool = parse_bool_field("final", True, event_name, event_data)
    micro: Optional[Dict] = None
    try:
        micro = event_data["micro"]
    except KeyError:
        pass

    event = events.create(event_name, is_start, is_final)

    # XXX: this causes a bug
    try:
        _parse_triggers(micro, event, components, triggers)
    except TriggersListDuplicatedError as err:
        raise OperationDeclError(
            names=[event_name], reason=f"{event_name} already exists!"
        )
    except OperationDeclError:
        raise
    except ShelleyParserError as err:
        raise OperationDeclError(names=[event_name], parent=err)

    assert event is not None
    return event


def _parse_events(
    src: Mapping,
    events: Events,
    components: Components,
    triggers: Triggers,
    behaviors: Behaviors,
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
    if not isinstance(src_events, dict):
        raise ShelleyParserError(
            title="syntax error in operation declarations section",
            reason=f"Expecting a dictionary but found {type(src_events).__name__}: {src_events!r}",
        )
    for event_name, event_data in src_events.items():
        if isinstance(event_data, dict):
            _parse_event(
                event_name=event_name,
                event_data=event_data,
                events=events,
                components=components,
                triggers=triggers,
            )
        else:
            raise ShelleyParserError(
                title="invalid operation declaration",
                reason=f"Expecting a dictionary but found: {event_data!r}",
            )

    for event_name, event_data in src_events.items():
        try:
            e1: Event = events[event_name]
            for e2 in _parse_event_list(event_data, "next", events):
                try:
                    behaviors.create(e1, e2)
                except BehaviorsListDuplicatedError:
                    raise OperationDeclError(
                        names=[event_name],
                        reason=f"Repeated operation {event_name!r} in section 'next'",
                        hints=["Ensure that there are no repeated operations in list."],
                    )
        except ShelleyParserError as err:
            raise OperationDeclError(names=[event_name], parent=err)


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
        raise OperationDeclError(
            names=[event.name],
            reason="Invalid integration rule. Only declare an integration rule when there are components (system has 0 components).",
            hints=["remove integration rule or declare a component."],
        )
    elif (
        src is None and len(components) > 0
    ):  # composition device not declaring micro for this event (not allowed!)
        count = len(components)
        raise OperationDeclError(
            names=[event.name],
            reason=f"Integration rule missing. Only declare an integration rule when there are components (system has {count} components).",
            hints=["write integration rule or remove all components."],
        )
    elif src is None and len(components) == 0:  # simple device without micro (ok!)
        trigger_rule = TriggerRuleFired()
    elif (
        src is not None and len(components) > 0
    ):  # composition device declaring trigger for this event (ok!)
        # try:
        trigger_rule = _parse_trigger_rule(src, components)
        # except ShelleyParserError as err:
        #    raise OperationDeclError(
        #        names=[event.name],
        #        parent=err
        #    )
    else:
        raise OperationDeclError(
            names=[event.name], reason=f"unknown option for operation: {src!r}"
        )

    assert trigger_rule is not None

    triggers.create(event, trigger_rule)


def _parse_trigger_rule(src, components: Components) -> TriggerRule:
    if src is None:
        raise IntegrationRuleError(reason=f"Micro must not be empty!")

    if isinstance(src, str):
        try:
            c_name, e_name = src.split(".")
        except ValueError as err:
            raise IntegrationRuleError(
                reason=f"Invalid micro rule {src!r}", hints=["Missing component?"]
            )
        component = components[c_name]
        assert component is not None
        return TriggerRuleEvent(component, e_name)
    elif isinstance(src, list) and len(src) == 0:
        raise EmptySequenceError()
    elif isinstance(src, list) and len(src) == 1:
        return _parse_trigger_rule(src.pop(0), components)
    elif isinstance(src, list):
        left = _parse_trigger_rule(src.pop(0), components)
        right = _parse_trigger_rule(src, components)
        return TriggerRuleSequence(left, right)
    elif isinstance(src, dict) and len(src) == 0:
        raise EmptySequenceError()
    elif isinstance(src, dict):
        if "xor" in src:
            trule_choice = TriggerRuleChoice()
            if src["xor"] is None:
                raise IntegrationRuleError(reason="xor must have at least one option!")
            for option in src["xor"]:
                trule_choice.choices.append(_parse_trigger_rule(option, components))
            return trule_choice
        elif "seq" in src:
            if src["seq"] is None:
                raise IntegrationRuleError(reason="seq must have at least one option!")
            left = _parse_trigger_rule(src["seq"].pop(0), components)
            if len(src["seq"]) > 0:
                right = _parse_trigger_rule(src["seq"], components)
                return TriggerRuleSequence(left, right)
            else:
                return left
        else:
            raise IntegrationRuleError(reason=f"Unknown option {src!r}")
    else:
        raise IntegrationRuleError(reason="Unknown option {src!r}")


def _create_device_from_yaml(yaml_code: Dict) -> Device:
    try:
        device_name = yaml_code["device"]["name"]
    except KeyError:
        raise SystemDeclError("Device must have a name")

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
        raise SystemDeclError("Missing key 'ok' for test macro!")

    try:
        test_macro["fail"]
    except KeyError:
        raise SystemDeclError("Missing key 'fail' for test macro!")

    try:
        test_micro = yaml_code["test_micro"]
    except KeyError:
        test_micro = {"ok": dict(), "fail": dict()}

    try:
        test_micro["ok"]
    except KeyError:
        raise SystemDeclError("Missing key 'ok' for test micro!")

    try:
        test_micro["fail"]
    except KeyError:
        raise SystemDeclError("Missing key 'fail' for test micro!")

    events: Events = Events()
    behaviors: Behaviors = Behaviors()
    components: Components = Components()
    triggers: Triggers = Triggers()
    _parse_components(device_components, components)
    _parse_events(
        src=copy.deepcopy(device_events),
        events=events,
        components=components,
        triggers=triggers,
        behaviors=behaviors,
    )
    _found_events_count: int = len(events)
    # _parse_behavior(device_behavior, events, behaviors, components, triggers)

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

    device = Device(device_name, events, behaviors, triggers, components=components,)

    device.test_macro = test_macro
    device.test_micro = test_micro

    return device


def get_shelley_from_yaml(path: pathlib.Path) -> Device:
    with path.open(mode="r") as stream:
        yaml_code = yaml.load(stream, MySafeLoader)
    return _create_device_from_yaml(yaml_code)


def get_shelley_from_yaml_str(yaml_str: str) -> Device:
    return _create_device_from_yaml(yaml.load(yaml_str, MySafeLoader))
