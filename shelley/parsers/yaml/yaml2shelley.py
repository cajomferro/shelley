import yaml
from typing import (
    List,
    Mapping,
    Dict,
    Optional,
    Union,
    Set,
    Iterable,
    Collection,
    Any,
    NoReturn,
    TypeVar,
    Type,
)
import copy
import pathlib
from dataclasses import dataclass, field

from shelley.parsers.yaml.util import MySafeLoader
from shelley.ast.events import Event, Events
from shelley.ast.actions import Actions, Action
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


def _parse_event_list(
    data: dict,
    key: str,
    events: Events,
) -> List[Event]:
    ANY = "$ANY"
    TITLE = f"section {key!r}"
    HINTS = [
        f"To list all operations write '{key}: {ANY}'",
    ]
    try:
        obj = data[key]
    except KeyError:
        raise ShelleyParserError(
            title=TITLE,
            reason=f"section {key!r} is missing",
            hints=HINTS,
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
    unknown_keys = set(event_data.keys()) - {KEY_MICRO, KEY_NEXT}
    if len(unknown_keys) > 0:
        raise OperationDeclError(
            names=[event_name], reason=f"remove unexpected keys: {unknown_keys!r}"
        )

    micro: Optional[Dict] = None
    try:
        micro = event_data[KEY_MICRO]
    except KeyError:
        pass

    event = events.create(event_name, False, False)

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

    src_events = copy.deepcopy(src)
    if not isinstance(src_events, dict):
        raise ShelleyParserError(
            title="syntax error in operation declarations section",
            reason=f"Expecting a dictionary but found {type(src_events).__name__}: {src_events!r}",
        )
    for event_name, event_data in src_events.items():
        if event_data is not None and isinstance(event_data, dict):
            _parse_event(
                event_name=event_name,
                event_data=event_data,
                events=events,
                components=components,
                triggers=triggers,
            )
        else:
            raise ShelleyParserError(
                title=f"error parsing operation {event_name!r}",
                reason=f"Expecting a dictionary but found: {event_data!r}",
            )

    for event_name, event_data in src_events.items():
        try:
            e1: Event = events[event_name]
            e2_events: List[Event] = _parse_event_list(event_data, KEY_NEXT, events)
            for e2 in e2_events:
                try:
                    behaviors.create(e1, e2)
                except BehaviorsListDuplicatedError:
                    raise OperationDeclError(
                        names=[event_name],
                        reason=f"Repeated operation {e2.name!r} in section '{KEY_NEXT}'",
                        hints=["Ensure that there are no repeated operations in list."],
                    )
            if len(e2_events) == 0:
                behaviors.create(e1, None)
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
            reason="Invalid integration rule. Only declare an integration rule when there are subsystems (system has 0 subsystems).",
            hints=["remove integration rule or declare a component."],
        )
    elif (
        src is None and len(components) > 0
    ):  # composition device not declaring micro for this event (not allowed!)
        count = len(components)
        raise OperationDeclError(
            names=[event.name],
            reason=f"Integration rule missing. Only declare an integration rule when there are subsystems (system has {count} subsystems).",
            hints=["write integration rule or remove all subsystems."],
        )
    elif src is None and len(components) == 0:  # simple device without micro (ok!)
        trigger_rule = TriggerRuleFired()
    elif (
        src is not None and len(components) > 0
    ):  # composition device declaring trigger for this event (ok!)
        trigger_rule = _parse_trigger_rule(src, components)
    else:
        raise OperationDeclError(
            names=[event.name], reason=f"unknown option for operation: {src!r}"
        )

    assert trigger_rule is not None

    triggers.create(event, trigger_rule)


def _parse_trigger_rule(src, components: Components) -> TriggerRule:
    if src is None:
        raise IntegrationRuleError(reason=f"Section {KEY_MICRO} must not be empty!")

    if isinstance(src, str):
        try:
            c_name, e_name = src.split(".")
        except ValueError as err:
            raise IntegrationRuleError(
                reason=f"Invalid '{KEY_MICRO}' rule {src!r}",
                hints=["Missing component?"],
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


T = TypeVar("T")


@dataclass
class Parser:
    hints: List[str] = field(default_factory=list)

    def _error(self, title: str, reason: str) -> NoReturn:
        raise ShelleyParserError(title=title, reason=reason, hints=self.hints)

    def _wrap_error(self, title: str, error: ShelleyParserError) -> NoReturn:
        raise ShelleyParserError(title=title, parent=error)

    def dict_get(self, data: Dict[Any, Any], key: str) -> Any:
        try:
            return data[key]
        except KeyError:
            self._error(title=f"section {key!r} error", reason="section is undeclared")

    def expect_type(self, obj: Any, ty: Type[T]) -> T:
        if obj is not None and isinstance(obj, ty):
            return obj
        self._error(
            title="type mismatch",
            reason=f"expecting a {ty.__name__} but got {type(obj).__name__}: {obj!r}",
        )

    def expect_opt_type(self, obj: Any, ty: Type[T]) -> Optional[T]:
        if obj is None or isinstance(obj, ty):
            return obj
        self._error(
            title="type mismatch",
            reason=f"expecting a {ty.__name__} or 'null' but got {type(obj).__name__}: {obj!r}",
        )

    def dict_get_str(self, data: Dict[Any, Any], key: str) -> str:
        obj = self.dict_get(data, key)
        try:
            return self.expect_type(obj, str)
        except ShelleyParserError as err:
            self._wrap_error(title=f"section {key!r} error", error=err)


KEY_NAME = "name"
KEY_START = "start_with"
KEY_END = "end_with"
KEY_SUBSYSTEMS = "subsystems"
KEY_OPS = "operations"
KEY_MICRO = "integration"
KEY_NEXT = "next"
KEY_TEST_SYS = "test_system"
KEY_TEST_INT = "test_integration"
KEY_TEST_OK = "ok"
KEY_TEST_FAIL = "fail"
KEY_ACTIONS = "outputs"


def _create_device_from_yaml(yaml_code: Dict) -> Device:
    EXPECTED_KEYS = {
        KEY_START,
        KEY_END,
        KEY_SUBSYSTEMS,
        KEY_TEST_SYS,
        KEY_TEST_INT,
        KEY_OPS,
        KEY_NAME,
        KEY_ACTIONS,
    }
    unexpected_keys = set(yaml_code.keys()) - EXPECTED_KEYS
    if len(unexpected_keys) > 0:
        raise ShelleyParserError(
            title=f"Unexpected section names: {unexpected_keys}",
            reason=f"Expected: {EXPECTED_KEYS}",
        )
    p = Parser()
    device_name = p.dict_get_str(yaml_code, KEY_NAME)

    device_components = yaml_code.get(KEY_SUBSYSTEMS, dict())
    device_events = yaml_code.get(KEY_OPS, dict())

    try:
        device_actions = yaml_code.get(KEY_ACTIONS, dict())
    except KeyError:
        device_actions = dict()
        pass  # actions are optional for now

    test_macro = yaml_code.get(
        KEY_TEST_SYS, {KEY_TEST_OK: dict(), KEY_TEST_FAIL: dict()}
    )

    try:
        test_macro[KEY_TEST_OK]
    except KeyError:
        raise SystemDeclError(f"Missing key '{KEY_TEST_OK}' for {KEY_TEST_SYS}!")

    try:
        test_macro[KEY_TEST_FAIL]
    except KeyError:
        raise SystemDeclError(f"Missing key '{KEY_TEST_FAIL}' for {KEY_TEST_SYS}!")

    test_micro = yaml_code.get(
        KEY_TEST_INT, {KEY_TEST_OK: dict(), KEY_TEST_FAIL: dict()}
    )

    try:
        test_micro[KEY_TEST_OK]
    except KeyError:
        raise SystemDeclError(f"Missing key '{KEY_TEST_OK}' for {KEY_TEST_INT}!")

    try:
        test_micro[KEY_TEST_FAIL]
    except KeyError:
        raise SystemDeclError(f"Missing key '{KEY_TEST_FAIL}' for {KEY_TEST_INT}!")

    events: Events = Events()
    actions: Actions = Actions()
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

    starts_with = set(ev.name for ev in _parse_event_list(yaml_code, KEY_START, events))
    ends_with = set(ev.name for ev in _parse_event_list(yaml_code, KEY_END, events))
    for evt in events.list():
        evt.is_start = evt.name in starts_with
        evt.is_final = evt.name in ends_with
    _found_events_count: int = len(events)

    # TODO: not required if we create empty micro for auto discovered event in behaviors
    # if len(components) > 0 and len(events) != _found_events_count:
    #     raise ShelleyParserError(
    #         "Device with components must explicitly declare all events"
    #     )

    # if not specified, first event is the start event
    # if len(events.start_events()) == 0:
    #    first_event = events.list()[0]
    #    first_event.is_start = True

    # we do not allow triggers without at least one trigger rule
    for event in events.list():
        assert triggers.get_rule(event.name) is not None

    # at this point, this must be true
    assert len(events) == len(triggers)

    for action_name in device_actions:
        if action_name not in events.list_str():
            raise SystemDeclError(f"Undeclared output event '{action_name}'!")
        actions.add(Action(action_name))

    device = Device(
        device_name, events, behaviors, triggers, components=components, actions=actions
    )

    device.test_macro = test_macro
    device.test_micro = test_micro

    return device


def get_shelley_from_yaml(path: pathlib.Path) -> Device:
    with path.open(mode="r") as stream:
        yaml_code = yaml.load(stream, MySafeLoader)
    return _create_device_from_yaml(yaml_code)


def get_shelley_from_yaml_str(yaml_str: str) -> Device:
    return _create_device_from_yaml(yaml.load(yaml_str, MySafeLoader))
