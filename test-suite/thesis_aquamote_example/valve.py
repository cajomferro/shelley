from shelley.shelleypy import system, claim, op, op_initial, op_initial_final, op_final
from machine import Pin


# we always close (note: this is overlap by the behavior itself)
@claim("system check G(open -> F ((close)));")
# we cannot close immediately after testing (next=["open", "clean", "test", "close"] to see the error)
@claim("system check G ((test -> ((X (open | clean)) & (X (! close)))) | END);")
# R2 # we cannot open immediately after cleaning (change next=["test", "open"] to see the error)
@claim("system check G ((clean & (! END)) -> (X (! open)));")
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
