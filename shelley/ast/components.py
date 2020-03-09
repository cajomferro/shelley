from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict

from .node import Node

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
if TYPE_CHECKING:
    from ast.visitors import Visitor
    from ast.devices import Device


class Component(Node):
    device = None  # type: Device
    name = None  # type: str

    def __init__(self, device: Device, name: str):
        self.device = device
        self.name = name

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_component(self)

    def check(self, uses_devices: List[str], devices: Dict[str, Device], components: List[Component]):
        self.check_device_in_uses(uses_devices)
        self.check_type_is_declared(devices)
        self.check_duplicates(components)
        components.append(self)

    def check_device_in_uses(self, uses_devices: List[str]):
        if self.device.name not in uses_devices:
            raise ComponentsDeviceNotUsedError("Device type '{0}' must be in uses list!".format(self.device.name))

    def check_type_is_declared(self, devices: Dict[str, Device]):
        if self.device.name not in devices:
            raise ComponentsDeviceNotUsedError("Device type '{0}' must be in uses list!".format(self.device.name))

    def check_duplicates(self, components: List[Component]):
        if self in components:
            raise ComponentsListDuplicatedError(
                "Duplicated component: '{0}'".format(self.name))

    def __eq__(self, other):
        if not isinstance(other, Component):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Component type")

        return self.name == other.name  # and self.device_name == other.device_name


class ComponentsListEmptyError(Exception):
    pass


class ComponentsListDuplicatedError(Exception):
    pass


class ComponentsDeviceNotUsedError(Exception):
    pass


class ComponentsDeviceNotDeclaredError(Exception):
    pass
