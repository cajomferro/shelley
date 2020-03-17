from .context import shelley
import pytest

from .creator.correct import DTimer, DButton, DLed
from shelley.ast.components import Component, Components
from shelley.ast.actions import Action, Actions, ActionsListDuplicatedError
from shelley.ast.events import GenericEvent, IEvent, EEvent, EEvents, IEvents, EventsListDuplicatedError


def test_create_components():
    components = Components()
    component_ledA = components.create("ledA", DLed.name)
    component_ledB = components.create("ledB", DLed.name)
    component_b = components.create("b", DButton.name)
    component_t = components.create("t", DTimer.name)

    assert ([component.name for component in components._data] == ['ledA', 'ledB', 'b', 't'])
    assert (components.count() == 4)
    assert (components.get_device_name(component_ledA.name) == 'LED')
    assert (component_ledA in components._data)


def test_create_action():
    actions = Actions()

    # create and add to Actions
    action1 = actions.create("turnOn")
    assert (actions.count() == 1)

    # create and reject duplicated on Actions
    with pytest.raises(ActionsListDuplicatedError):
        actions.create("turnOn")

    # create and then add to Actions
    action3 = Action("turnOff")
    actions.add(action3)
    assert (actions.count() == 2)

    action4 = Action("nowhere")

    assert (action1 != action3)

    assert (actions.contains(action1) is True)
    assert (actions.contains(action3) is True)
    assert (actions.contains(action4) is False)

    assert (actions.find_by_name(action1.name) == action1)
    assert (actions.find_by_name(action3.name) == action3)
    assert (actions.find_by_name(action4.name) is None)


def test_create_ievents():
    events = IEvents()

    # create and add to Actions
    eon = events.create("on")
    assert (events.count() == 1)

    # create and reject duplicated on Events
    with pytest.raises(EventsListDuplicatedError):
        events.create("on")

    # create and then add to Events
    eoff = IEvent("off")
    events.add(eoff)
    assert (events.count() == 2)

    enowwhere = IEvent("nowhere")

    assert (eon != eoff)

    assert (events.contains(eon) is True)
    assert (events.contains(eoff) is True)
    assert (events.contains(enowwhere) is False)

    assert (events.find_by_name(eon.name) == eon)
    assert (events.find_by_name(eoff.name) == eoff)
    assert (events.find_by_name(enowwhere.name) is None)


def test_create_ievents():
    events = EEvents()

    # create and add to Actions
    eon = events.create("on")
    assert (events.count() == 1)

    # create and reject duplicated on Events
    with pytest.raises(EventsListDuplicatedError):
        events.create("on")

    # create and then add to Events
    eoff = EEvent("off")
    events.add(eoff)
    assert (events.count() == 2)

    enowwhere = EEvent("nowhere")

    assert (eon != eoff)

    assert (events.contains(eon) is True)
    assert (events.contains(eoff) is True)
    assert (events.contains(enowwhere) is False)

    assert (events.find_by_name(eon.name) == eon)
    assert (events.find_by_name(eoff.name) == eoff)
    assert (events.find_by_name(enowwhere.name) is None)


def test_create_mixevents():
    eevent1 = EEvent("on")
    eevent2 = IEvent("on")

    assert (eevent1 != eevent2)
