from shelleypy import operation, system, claim
from machine import Pin


@claim("system check G(on -> F ((off)));")
@system(uses={})
class LED:
    def __init__(self):
        self.led = Pin(27, Pin.OUT)
        self.brightness = "min"

    @operation(initial=True, next=["off"])
    def on(self):
        self.led.on()
        return "off"

    @operation(final=True, next=["on"])
    def off(self):
        self.led.off()
        return "on"

    @operation(initial=True, final=True, next=["on"])
    def set_brightness(self, brightness="max"):
        self.led.brightness = brightness
        return "on"