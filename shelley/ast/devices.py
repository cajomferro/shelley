from __future__ import annotations
from typing import Mapping, List, TYPE_CHECKING, Optional

from shelley.ast.node import Node
from shelley.ast.actions import Actions
from shelley.ast.behaviors import Behaviors
from shelley.ast.components import Components
from shelley.ast.triggers import Triggers
from shelley.ast.events import IEvents, EEvents, Events

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
    internal_events: IEvents
    external_events: EEvents
    start_events: List[str]
    behaviors: Behaviors
    uses: List[str]
    components: Components
    triggers: Triggers
    test_macro: Mapping[str, Mapping[str, List[str]]]
    test_micro: Mapping[str, Mapping[str, List[str]]]

    def __init__(
        self,
        name: str,
        actions: Actions,
        internal_events: IEvents,
        external_events: EEvents,
        start_events: List[str],
        behaviors: Behaviors,
        triggers: Triggers,
        uses: Optional[List[str]] = None,
        components: Optional[Components] = None,
    ) -> None:
        if uses is None:
            uses = []
        if components is None:
            components = Components()
        self.name = name
        self.actions = actions
        self.internal_events = internal_events
        self.external_events = external_events
        self.start_events = start_events
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

    def get_all_events(self) -> Events:
        return self.external_events.merge(self.internal_events)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Device):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Device type")

        return self.name == other.name


class DevicesListDuplicatedError(Exception):
    pass
