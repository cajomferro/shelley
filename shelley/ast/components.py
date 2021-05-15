from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Optional
from dataclasses import dataclass

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
                f"Device type '{device_name}' must be in uses list!"
            )

    def check_type_is_declared(self, devices: Dict[str, Device], device_name: str):
        if device_name not in devices:
            raise ComponentsDeviceNotUsedError(
                f"Device type '{device_name}' must be in uses list!"
            )

    def __str__(self):
        return self.name


class ComponentsListEmptyError(Exception):
    pass


class ComponentsListDuplicatedError(Exception):
    pass


class ComponentsDeviceNotUsedError(Exception):
    pass


class ComponentsDeviceNotDeclaredError(Exception):
    pass


class Components(Node):
    _data: List[Component]
    components_to_devices: Dict[str, str]

    def __init__(self) -> None:
        self._data = []
        self.components_to_devices = dict()

    def add(self, elem: Component) -> None:
        if elem not in self._data:
            self._data.append(elem)
        else:
            raise ComponentsListDuplicatedError()

    def contains(self, elem: Component) -> bool:
        return elem in self._data

    def list(self) -> List[Component]:
        return self._data

    def __iter__(self):
        return iter(self.components_to_devices.items())

    def list_str(self) -> List[str]:
        return [str(elem) for elem in self._data]

    def __len__(self):
        return len(self._data)

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
