from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Optional
from dataclasses import dataclass

from shelley.ast.util import MyCollection
from shelley.ast.node import Node

# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor
    from shelley.ast.devices import Device


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

    def check(self, uses: List[str], devices: Dict[str, Device], device_name: str):
        self.check_device_in_uses(uses, device_name)
        self.check_type_is_declared(devices, device_name)

    def check_device_in_uses(self, uses: List[str], device_name: str):
        if device_name not in uses:
            raise ComponentsDeviceNotUsedError(
                "Device type '{0}' must be in uses list!".format(device_name)
            )

    def check_type_is_declared(self, devices: Dict[str, Device], device_name: str):
        if device_name not in devices:
            raise ComponentsDeviceNotUsedError(
                "Device type '{0}' must be in uses list!".format(device_name)
            )

    def __str__(self):
        return self.name

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


class Components(MyCollection[Component]):
    components_to_devices: Dict[str, str]

    def __init__(self) -> None:
        super().__init__()
        self.components_to_devices = dict()

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

    def find_by_name(self, name: str) -> Optional[Component]:
        re: Optional[Component] = None
        try:
            re = next(x for x in self._data if x.name == name)
        except StopIteration:
            pass
        return re

    def __getitem__(self, name: str) -> Component:
        res = self.find_by_name(name)
        if res is None:
            raise KeyError(name)
        return res

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_components(self)
