import shelley
import pytest

from .creator.correct import DTimer, DButton, DLed
from shelley.ast.components import Component, Components, ComponentsListDuplicatedError
from shelley.ast.actions import Action, Actions, ActionsListDuplicatedError
from shelley.ast.events import (
    GenericEvent,
    IEvent,
    EEvent,
    EEvents,
    IEvents,
    EventsListDuplicatedError,
)
from shelley.ast.triggers import Trigger, Triggers, TriggersListDuplicatedError
from shelley.ast.rules import TriggerRuleFired


def test_create_triggers() -> None:
    event_a = GenericEvent("a")
    event_b = GenericEvent("a")
    triggers = Triggers()
    triggers.create(event_a, TriggerRuleFired())
    assert triggers.count() == 1

    with pytest.raises(TriggersListDuplicatedError):
        triggers.create(event_a, TriggerRuleFired())

    with pytest.raises(TriggersListDuplicatedError):
        triggers.create(event_b, TriggerRuleFired())

    assert triggers.count() == 1


def test_create_components() -> None:
    components = Components()
    component_ledA = components.create("ledA", DLed.name)
    component_ledB = components.create("ledB", DLed.name)
    component_b = components.create("b", DButton.name)
    component_t = components.create("t", DTimer.name)

    assert [component.name for component in components._data] == [
        "ledA",
        "ledB",
        "b",
        "t",
    ]
    assert components.count() == 4
    assert components.get_device_name(component_ledA.name) == "Led"
    assert component_ledA in components._data

    with pytest.raises(ComponentsListDuplicatedError):
        component_dup = components.create("ledA", DLed.name)


def test_create_action() -> None:
    actions = Actions()

    # create and add to Actions
    action1 = actions.create("turnOn")
    assert actions.count() == 1

    # create and reject duplicated on Actions
    with pytest.raises(ActionsListDuplicatedError):
        actions.create("turnOn")

    # create and then add to Actions
    action3 = Action("turnOff")
    actions.add(action3)
    assert actions.count() == 2

    action4 = Action("nowhere")

    assert action1 != action3

    assert actions.contains(action1) is True
    assert actions.contains(action3) is True
    assert actions.contains(action4) is False

    assert actions.find_by_name(action1.name) == action1
    assert actions.find_by_name(action3.name) == action3
    assert actions.find_by_name(action4.name) is None


def test_create_ievents() -> None:
    events = IEvents()

    # create and add to Actions
    eon = events.create("on")
    assert events.count() == 1

    # create and reject duplicated on Events
    with pytest.raises(EventsListDuplicatedError):
        events.create("on")

    # create and then add to Events
    eoff = IEvent("off")
    events.add(eoff)
    assert events.count() == 2

    enowwhere = IEvent("nowhere")

    assert eon != eoff

    assert events.contains(eon) is True
    assert events.contains(eoff) is True
    assert events.contains(enowwhere) is False

    assert events.find_by_name(eon.name) == eon
    assert events.find_by_name(eoff.name) == eoff
    assert events.find_by_name(enowwhere.name) is None


def test_create_mixevents() -> None:
    eevent1 = EEvent("on")
    eevent2 = IEvent("on")

    assert eevent1 != eevent2
