from .counter import Counter
from .led import LED
from shelley.shelleypy import (
    operation,
    system,
    claim,
)


# @claim(
#     "system check G (s1test -> F ((step1_handle_error & END) | (step1_stop & END) | (step2 & END)));"
# )  # R1
# @claim(
#     "integration check G ( (a.open -> F(t.wait & F a.close)) & (b.open -> F(t.wait & F b.close)));"
# )  # R2
# @claim("subsystem va check G (test -> X !test);")  # R3
# # @claim("subsystem vb check G (error -> X clean);") # this is false!
@system(uses={"c": "Counter", "l": "LED"})
class Controller:
    def __init__(self, valve_a_first_off: bool = True):
        self.c = Counter()
        self.l = LED()

    @operation(initial=True, next=["click2"])
    async def click1(self):
        await self.l.on()
        await self.c.inc()
        return "click2"

    @operation(final=True, next=["click1"])
    async def click2(self):
        await self.l.off()
        await self.c.inc()
        return "click1"
