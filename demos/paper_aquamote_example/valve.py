from shelley.shelleypy import operation, system, claim, op_initial, op_final
from machine import Pin

@system(uses={})
class Valve:
    def __init__(self, port):
        self._pin = Pin(27, Pin.OUT)

    @op_initial
    def on(self):
        self._pin.open()
        return ["off"]

    @op_final
    def off(self):
        self._pin.close()
        return ["on"]
