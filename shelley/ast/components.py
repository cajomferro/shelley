from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Set
import uuid

from .node import Node

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
if TYPE_CHECKING:
    from ast.visitors import Visitor
    from .devices import Device


class Component(Node):
    uuid = uuid.uuid1()
    name = None  # type: str

    def __init__(self, name: str):
        self.name = name

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_component(self)

    def check(self, uses: Set[str], devices: Dict[str, Device],
              device_name: str):
        self.check_device_in_uses(uses, device_name)
        self.check_type_is_declared(devices, device_name)

    def check_device_in_uses(self, uses: Set[str], device_name: str):
        if device_name not in uses:
            raise ComponentsDeviceNotUsedError("Device type '{0}' must be in uses list!".format(device_name))

    def check_type_is_declared(self, devices: Dict[str, Device], device_name: str):
        if device_name not in devices:
            raise ComponentsDeviceNotUsedError("Device type '{0}' must be in uses list!".format(device_name))

    def __eq__(self, other):
        if not isinstance(other, Component):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Component type")

        return self.name == other.name

    def __hash__(self):
        return id(self.uuid)


class ComponentsListEmptyError(Exception):
    pass


class ComponentsListDuplicatedError(Exception):
    pass


class ComponentsDeviceNotUsedError(Exception):
    pass


class ComponentsDeviceNotDeclaredError(Exception):
    pass
