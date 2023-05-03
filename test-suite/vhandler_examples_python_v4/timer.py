from api import asyncio
from shelley.shelleypy import operation, system, claim


@system(uses={})
class Timer:
    def __init__(self, period_ms=1000):
        self.period_ms = period_ms

    @operation(initial=True, final=True, next=["wait"])
    async def wait(self):
        await asyncio.sleep_ms(self.period_ms)
