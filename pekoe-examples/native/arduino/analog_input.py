from native.arduino import Arduino
from native.generic.analog_input import AnalogInput
from typing import Callable  # https://docs.python.org/3/library/typing.html#callable


class ArduinoAnalogInput(AnalogInput):
    pin = None

    def __init__(self, pin: int):
        super()
        self.pin = pin

    def attach_fall(self, callback: Callable[[], None]):
        Arduino.pinMode(self.pin, Arduino.INPUT)
        Arduino.attachInterruptOnce(
            self.pin, lambda: self._isr(AnalogInput.FALL), Arduino.FALL
        )
        self.subscribe(AnalogInput.FALL, callback)

    def attach_rise(self, callback: Callable[[], None]):
        Arduino.pinMode(self.pin, Arduino.INPUT)
        Arduino.attachInterruptOnce(
            self.pin, lambda: self._isr(AnalogInput.RISE), Arduino.RISE
        )
        self.subscribe(AnalogInput.RISE, callback)

    def isr(self, event):
        self.raise_event(event)
