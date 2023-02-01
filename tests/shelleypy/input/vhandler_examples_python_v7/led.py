from machine import Pin
from shelleypy import operation, system, claim

# we always close (note: this is overlap by the behavior itself)
#@claim("system check G(open -> F ((close)));")
# we cannot close immediately after testing (next=["open", "clean", "test", "close"] to see the error)
#@claim("system check G ((test -> ((X (open | clean)) & (X (! close)))) | END);")
# R2 # we cannot open immediately after cleaning (change next=["test", "open"] to see the error)
#@claim("system check G ((clean & (! END)) -> (X (! open)));")
@system(uses={})
class LED:
    def __init__(self, pin='LED1'):
        self.led = Pin(pin, Pin.OUT)

    @operation(initial=True, next=["off"])
    def on(self):
        self.led.on()

    @operation(final=True, next=["on"])
    def off(self):
        self.led.off()

