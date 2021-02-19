from decorators import *
from devices import Device
from native.generic.analog_input import AnalogInput as ButtonNative


class ButtonDevice(Device):
    PRESSED = 0
    RELEASED = 1

    button_native = None

    def __init__(self, driver_id: str, button_native: ButtonNative):
        Device.__init__(self, driver_id)
        self.button_native = button_native
        self.button_native.attach_fall(self.button_pressed)

    @callback(ButtonNative.FALL)
    @raise_event(PRESSED)
    def button_pressed(self):
        self.button_native.attach_rise(self.button_released)
        self.raise_event(self.PRESSED)

    @callback(ButtonNative.RISE)
    @raise_event(RELEASED)
    def button_released(self):
        self.button_native.attach_rise(self.button_pressed)
        self.raise_event(self.RELEASED)
