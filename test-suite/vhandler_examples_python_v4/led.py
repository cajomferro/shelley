from api import asyncio
from hw import HWLED
import operation, primitive_system


@primitive_system
class LED:
    def __init__(self, period_ms=1000):
        self._led = HWLED()

    @operation(initial=True, next=["blink", "off"])
    async def on(self):
        self._led.on()

    @operation(initial=True, next=["off"])
    async def blink(self):
        self._led.blink()  # probably this is implemented with async

    @operation(final=True, next=["on", "blink"])
    async def off(self):
        self._led.off()
