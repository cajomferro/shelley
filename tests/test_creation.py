from .context import shelley

from .creator.correct import DTimer, DButton, DLed
from shelley.ast.components import Component
from shelley.ast.actions import Action
from shelley.ast.events import GenericEvent, IEvent, EEvent


def test_create_components():
    components = {
        Component("ledA"): DLed.name,
        Component("ledA"): DLed.name,
        Component("ledB"): DLed.name,
        Component("b"): DButton.name,
        Component("t"): DTimer.name
    }
    assert ([component.name for component in components.keys()] == ['ledA', 'ledB', 'b', 't'])
    assert (len(components) == 4)
    assert (components[Component("ledA")] == 'LED')
    assert (Component("ledA") in components)


def test_create_action():
    action1 = Action("turnOn")
    action2 = Action("turnOn")
    action3 = Action("turnOff")

    assert (action1 is action2)
    assert (action1 == action2)
    assert (action1 is not action3)

    actions = set()
    actions.add(action1)
    actions.add(action2)
    assert (len(actions) == 1)
    actions.add(action3)
    assert (len(actions) == 2)

    assert (action1 in actions)
    assert (action2 in actions)


def test_create_ievents():
    ievent1 = IEvent("on")
    ievent2 = IEvent("on")
    ievent3 = IEvent("off")

    assert (ievent1 is ievent2)
    assert (ievent1 == ievent2)
    assert (ievent1 is not ievent3)

    events = set()
    events.add(ievent1)
    events.add(ievent2)
    assert (len(events) == 1)
    events.add(ievent3)
    assert (len(events) == 2)

    assert (ievent1 in events)
    assert (ievent2 in events)


def test_create_eevents():
    eevent1 = EEvent("on")
    eevent2 = EEvent("on")
    eevent3 = EEvent("off")

    assert (eevent1 is eevent2)
    assert (eevent1 == eevent2)
    assert (eevent1 is not eevent3)

    events = set()
    events.add(eevent1)
    events.add(eevent2)
    assert (len(events) == 1)
    events.add(eevent3)
    assert (len(events) == 2)

    assert (eevent1 in events)
    assert (eevent2 in events)


def test_create_mixevents():
    eevent1 = EEvent("on")
    eevent2 = IEvent("on")

    assert (eevent1 is eevent2)
    assert (eevent1 == eevent2)
