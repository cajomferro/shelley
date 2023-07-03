from shelley.shelleypy import system, op
from machine import Pin


@system(uses={})
class Valve:
    def __init__(self):
        self.control = Pin(27, Pin.OUT)
        self.clean = Pin(28, Pin.OUT)
        self.status = Pin(29, Pin.IN)

    @op(initial=True)
    def test(self):
        if self.status.value():
            return "open"
        else:
            return "clean"

    @op
    def open(self):
        self.control.on()
        return "close"

    @op(final=True)
    def close(self):
        self.control.off()
        return "test"

    @op(final=True)
    def clean(self):
        self.clean.on()
        return "test"

