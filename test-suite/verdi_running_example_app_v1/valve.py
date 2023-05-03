from shelley.shelleypy import operation, system, claim
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

    @operation(initial=True, next=["open", "clean"])
    def test(self):
        if self.status.value():
            return "open"
        else:
            return "clean"

    @operation(next=["close"])
    def open(self):
        self.control.on()
        return "close"

    @operation(final=True, next=["test"])
    def close(self):
        self.control.off()
        return "test"

    @operation(final=True, next=["test"])  # , "open"]) # R2
    def clean(self):
        self.clean.on()
        return "test"

    # @operation(next=["test"]) # unreachable operaiton
    # def foo(self):
    #     pass
