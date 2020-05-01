from __future__ import annotations
from typing import Mapping, List, TYPE_CHECKING, Optional

from shelley.ast.node import Node
from shelley.ast.actions import Actions
from shelley.ast.behaviors import Behaviors
from shelley.ast.components import Components
from shelley.ast.triggers import Triggers
from shelley.ast.events import Events

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


def discover_uses(components: Components) -> List[str]:
    uses = list()
    for component_name in components.components_to_devices:
        device_name = components.components_to_devices[component_name]
        if device_name not in uses:
            uses.append(device_name)
    return uses


class Device(Node):
    """
    \\hard{D} -> categoria sintática
    """

    name: str
    actions: Actions
    events: Events  # TODO: change to Events later
    behaviors: Behaviors
    uses: List[str]
    components: Components
    triggers: Triggers
    test_macro: Mapping[str, Mapping[str, List[str]]]
    test_micro: Mapping[str, Mapping[str, List[str]]]

    def __init__(
        self,
        name: str,
        events: Events,
        behaviors: Behaviors,
        triggers: Triggers,
        actions: Optional[Actions] = None,
        uses: Optional[List[str]] = None,
        components: Optional[Components] = None,
    ) -> None:
        if actions is None:
            actions = Actions()
        if uses is None:
            uses = []
        if components is None:
            components = Components()
        self.name = name
        self.actions = actions
        self.events = events
        self.behaviors = behaviors
        self.uses = uses
        self.components = components
        self.triggers = triggers

        # find used devices from components if not specified
        if len(self.uses) == 0 and len(self.components.components_to_devices) != 0:
            self.uses = discover_uses(self.components)

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_device(self)

    def check_is_duplicated(self, devices: List[Device]) -> None:
        if self in devices:
            raise DevicesListDuplicatedError(
                "Duplicated device with name '{0}'".format(self.name)
            )


    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Device):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Device type")

        return self.name == other.name


class DevicesListDuplicatedError(Exception):
    pass
