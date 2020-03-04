from typing import List, Dict

from devices import Device
from components import Component


class ComponentsListEmptyError(Exception):
    pass


class ComponentsListDuplicatedError(Exception):
    pass


class ComponentsDeviceNotUsedError(Exception):
    pass


class ComponentsDeviceNotDeclaredError(Exception):
    pass


def check(components: List[Component],
          uses_devices: List[str],
          declared_devices: Dict[str, Device]) -> Dict[str, Device]:
    return _check(components.copy(), uses_devices.copy(), declared_devices.copy())


def _check(components: List[Component],
           uses_devices: List[str],
           declared_devices: Dict[str, Device]) -> Dict[str, Device]:
    """

    :param components:
    :param uses_devices:
    :param declared_devices:
    :return: dict mapping component name to component (i.e., device) type (declared components)
    """
    if len(components) == 0:
        raise ComponentsListEmptyError("List of components cannot be empty!")

    tail = components.pop()  # type: Component

    if len(components) == 0:
        if tail.device.name not in uses_devices:
            raise ComponentsDeviceNotUsedError("Device type '{0}' must be in uses list!".format(tail.device.name))

        try:
            component_device = declared_devices[tail.device.name]  # type: Device
        except KeyError as error:
            raise ComponentsDeviceNotDeclaredError("Device type '{0}' has not been declared!".format(tail.device.name))

        return {tail.name: component_device}
    else:
        lambda_1 = _check([tail], uses_devices, declared_devices)
        lambda_2 = _check(components, uses_devices, declared_devices)

        if not lambda_1.keys().isdisjoint(lambda_2.keys()):
            raise ComponentsListDuplicatedError("Duplicated component: {0}".format(tail.name))

        return {**lambda_1, **lambda_2}  # merge dicts
