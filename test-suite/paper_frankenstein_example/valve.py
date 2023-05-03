from hw import HWValve
from shelley.shelleypy import operation, system, claim


@claim("system check on;")
@claim("system check F(off & END);")
@system(uses={})
class Valve:
    def __init__(self, port):
        self._valve = HWValve(port)

    @operation(initial=True, next=["off"])
    async def on(self):
        self._valve.on()

    @operation(final=True, next=["on"])
    async def off(self):
        self._valve.off()
