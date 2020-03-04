from typing import List, Dict, Tuple
from actions import Action
from events import GenericEvent, EEvent, IEvent
from behaviours import Behaviour
from components import Component
from triggers import TriggerRule, Trigger

from devices import Device
from actions.checker import check as check_actions
from events.checker import check as check_events
from behaviours.checker import check as check_behaviours
from components.checker import check as check_components
from triggers.checker import check as check_triggers


def create(declared_devices: Dict[str, Device], name: str, actions: List[Action], events: List[GenericEvent],
           behaviours: List[Behaviour], uses: List[str] = None, components: List[Component] = None,
           triggers: List[Trigger] = None) -> Device:
    """
    Create device object from parsed fields

    :param declared_devices:
    :param name:
    :param actions:
    :param events:
    :param behaviours:
    :param uses:
    :param components:
    :param triggers:
    :return:
    """
    device_actions = None  # type: Set[Action]
    if actions is not None:
        device_actions = check_actions(actions)

    declared_i_events, declared_e_events = check_events(events)  # type: List[IEvent], List[EEvent]

    behaviours_result = []  # type: List[Behaviour]
    check_behaviours(behaviours, actions, declared_i_events, declared_e_events,
                     behaviours_result)

    declared_components = check_components(components, uses, declared_devices)  # type: Dict[str, Device]

    triggers_result = []  # type: List[Trigger]
    check_triggers(triggers, declared_e_events, declared_components, triggers_result)

    device = Device(name, actions, declared_i_events, declared_e_events, behaviours, components, triggers)

    return device
