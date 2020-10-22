from native.arduino import Arduino
from native.generic.digital_output import DigitalOutput


class ArduinoDigitalOutput(DigitalOutput):
    pin = None

    def __init__(self, pin: int):
        super()
        self.pin = pin
        Arduino.pinMode(self.pin, Arduino.OUTPUT)

    def high(self):
        Arduino.digitalWrite(self.pin, Arduino.HIGH)

    def low(self):
        Arduino.digitalWrite(self.pin, Arduino.LOW)
