from shelley.shelleypy import system, claim, op_initial, op, op_final
from machine import Pin


@system(uses={})
class Valve:
    def __init__(self):
        self.control = Pin(27, Pin.OUT)
        self.clean = Pin(28, Pin.OUT)
        self.status = Pin(29, Pin.IN)

    @op_initial
    def test(self):
        if self.status.value():
            return "open"
        else:
            return "clean"

    @op
    def open(self):
        self.control.on()
        return "close"

    @op_final
    def close(self):
        self.control.off()
        return "test"

    @op_final
    def clean(self):
        self.clean.on()
        return "test"
