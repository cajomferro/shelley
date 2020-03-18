from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

from .util import MyCollection
from .node import Node
# from . import components, find_instance_by_name
from dataclasses import dataclass

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
if TYPE_CHECKING:
    from ast.visitors import Visitor
    from .devices import Device


@dataclass(order=True)
class Component(Node):
    name: str

    def accept(self, visitor: Visitor) -> None:
        """
        Note that we're calling `visitConcreteComponentA`, which matches the
        current class name. This way we let the visitor know the class of the
        component it works with.
        """

        visitor.visit_component(self)

    def check(self, uses: List[str], devices: Dict[str, Device],
              device_name: str):
        self.check_device_in_uses(uses, device_name)
        self.check_type_is_declared(devices, device_name)

    def check_device_in_uses(self, uses: List[str], device_name: str):
        if device_name not in uses:
            raise ComponentsDeviceNotUsedError("Device type '{0}' must be in uses list!".format(device_name))

    def check_type_is_declared(self, devices: Dict[str, Device], device_name: str):
        if device_name not in devices:
            raise ComponentsDeviceNotUsedError("Device type '{0}' must be in uses list!".format(device_name))

    # def __init__(self, name: str):
    #     self.name = name
    #
    # def __new__(cls, name: str):
    #     instance = find_instance_by_name(name, components)
    #     if instance is None:
    #         instance = super(Component, cls).__new__(cls)
    #         components.append(instance)
    #     return instance

    # def __eq__(self, other):
    #     if not isinstance(other, Component):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance is not of Component type")
    #
    #     return self.name == other.name
    #
    # def __hash__(self):
    #     return id(self.uuid)


class ComponentsListEmptyError(Exception):
    pass


class ComponentsListDuplicatedError(Exception):
    pass


class ComponentsDeviceNotUsedError(Exception):
    pass


class ComponentsDeviceNotDeclaredError(Exception):
    pass


class Components(Node, MyCollection[Component]):
    components_to_devices = None  # type: Dict[str, str]
    _data = None  # type: List[Component]

    def __init__(self):
        self.components_to_devices = dict()
        self._data = list()

    def create(self, component_name: str, device_name: str) -> Component:
        component = Component(component_name)
        if component not in self._data:
            self._data.append(component)
            self.components_to_devices[component_name] = device_name
        else:
            raise ComponentsListDuplicatedError()
        return component

    def get_device_name(self, component_name) -> str:
        return self.components_to_devices[component_name]

    def find_by_name(self, name: str) -> Component:
        re = None  # type: Component
        try:
            re = next(x for x in self._data if x.name == name)
        except StopIteration:
            pass
        return re

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_components(self)
