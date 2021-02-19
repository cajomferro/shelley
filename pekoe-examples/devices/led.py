from decorators import *
from devices import Device
from native.generic.digital_output import DigitalOutput as LEDNative


class LEDDevice(Device):
    ON = 0
    OFF = 1

    led_native = LEDNative

    def __init__(self, driver_id: str, led_native: LEDNative):
        Device.__init__(self, driver_id)
        self.led_native = led_native

    @action
    @raise_event(ON)
    def turn_on(self):
        self.led_native.high()
        self.raise_event(LEDDevice.ON)

    @action
    @raise_event(OFF)
    def turn_off(self):
        self.led_native.low()
        self.raise_event(LEDDevice.OFF)
