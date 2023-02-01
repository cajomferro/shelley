from shelley.shelleypy import operation, system, claim
from machine import Pin


@system(uses={})
class Valve:
    def __init__(self, port):
        self._pin = Pin(27, Pin.OUT)

    @operation(initial=True, next=["close"])
    def open(self):
        self._pin.open()
        return "close"

    @operation(final=True, next=["open"])
    def close(self):
        self._pin.close()
        return "open"
