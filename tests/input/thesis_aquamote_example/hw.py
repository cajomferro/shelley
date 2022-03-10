from machine import Pin

class HWLed:

    def __init__(self, pin_number):
        self._led = Pin(pin_number, Pin.OUT, value=1)

    def on(self):
        self._led.off()  # ESP32 is flipped

    def off(self):
        self._led.on()  # ESP32 is flipped