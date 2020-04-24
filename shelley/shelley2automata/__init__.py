from typing import Dict

from karakuri.regular import Regex

from shelley.automata import Device as AutomataDevice
from shelley.ast.devices import Device as ShelleyDevice
from shelley.ast.triggers import Triggers
from shelley.ast.visitors.trules2regex import TRules2RegexVisitor


def get_regex_dict(triggers: Triggers) -> Dict[str, Regex]:
    visitor = TRules2RegexVisitor()
    triggers.accept(visitor)
    regex_dict: Dict[str, Regex] = visitor.regex_dict
    return regex_dict


def shelley2automata(shelley_device: ShelleyDevice) -> AutomataDevice:
    return AutomataDevice(start_events=shelley_device.start_events,
                          events=shelley_device.get_all_events().list_str(),
                          behavior=shelley_device.behaviors.as_list_tuples(),
                          components=shelley_device.components.components_to_devices,
                          triggers=get_regex_dict(shelley_device.triggers))
