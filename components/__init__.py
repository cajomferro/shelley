# https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from devices import Device


class Component:
    device = None
    name = None  # type: str

    def __init__(self, device: Device, name: str):
        self.device = device
        self.name = name

        assert (name is not None), "Component name is None"
        assert (self.device.name is not None), "Device name is None"

    def __eq__(self, other):
        if not isinstance(other, Component):
            # don't attempt to compare against unrelated types
            raise Exception("Instance is not of Component type")

        return self.name == other.name  # and self.device_name == other.device_name
