from __future__ import annotations
from typing import Mapping, List, TYPE_CHECKING, Tuple
from dataclasses import dataclass, field

from shelley.ast.node import Node
from shelley.ast.actions import Actions
from shelley.ast.behaviors import Behaviors
from shelley.ast.components import Components
from shelley.ast.triggers import Triggers
from shelley.ast.events import Events
from shelley.parsers.ltlf_lark_parser import Formula

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


def discover_uses(components: Components) -> List[str]:
    uses = list()
    for component_name in components.components_to_devices:
        device_name = components.components_to_devices[component_name]
        if device_name not in uses:
            uses.append(device_name)
    return uses


@dataclass
class Device(Node):
    name: str
    events: Events
    behaviors: Behaviors
    triggers: Triggers
    actions: Actions = field(default_factory=Actions)
    uses: List[str] = field(default_factory=list)
    components: Components = field(default_factory=Components)
    test_macro: Mapping[str, Mapping[str, List[str]]] = field(default_factory=dict)
    test_micro: Mapping[str, Mapping[str, List[str]]] = field(default_factory=dict)
    enforce_formulae: List[Formula] = field(default_factory=list)
    system_formulae: List[Formula] = field(default_factory=list)
    integration_formulae: List[Formula] = field(default_factory=list)
    subsystem_formulae: List[Tuple[str, Formula]] = field(default_factory=list)

    def __post_init__(self) -> None:

        # find used devices from components if not specified
        if len(self.uses) == 0 and len(self.components.components_to_devices) != 0:
            self.uses = discover_uses(self.components)

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        return visitor.visit_device(self)

    def check_is_duplicated(self, devices: List[Device]) -> None:
        if self in devices:
            raise DevicesListDuplicatedError(
                "Duplicated device with name '{0}'".format(self.name)
            )

    def __eq__(self, other: object) -> bool:
        if other is None or not isinstance(other, Device):
            return False
        return (
            self.name == other.name
            and self.actions == other.actions
            and self.events == other.events
            and self.behaviors == other.behaviors
            and self.uses == other.uses
            and self.components == other.components
            and self.triggers == other.triggers
        )


class DevicesListDuplicatedError(Exception):
    pass
