from .led import LED
from shelleypy import operation, system, claim

@claim("integration check G(led.set_brightness -> F (led.off | END));")
@claim("integration check G(led.on -> X (led.off));")
@claim("integration check F (led.on & X led.off);")
# @claim("integration check F led.on & F led.off;")
@system(uses={"led": "LED"})
class App:

    def __init__(self):
        self.led = LED()

    @operation(initial=True, next=["blink"])
    def start(self, brightness=None):
        if brightness:
            self.led.set_brightness(brightness)
            return "blink"
        else:
            return "blink"

    @operation(final=True, next=[])
    def blink(self):
        self.led.on() # force at least one time (omitting this violates claim)
        self.led.off()
        for i in range(10):
            self.led.on()
            self.led.off()
        
        return ""


