from hw import HWLED
from shelley.shelleypy import operation, system, claim


@claim("system check F (off & END);")
@system(uses={})
class LED:
    def __init__(self, port: int):
        self._led = HWLED(port=port)

    @operation(initial=True, next=["off"])
    async def on(self):
        self._led.on()

    @operation(final=True, next=["on"])
    async def off(self):
        self._led.off()
