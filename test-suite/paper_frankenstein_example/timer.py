import asyncio
from hw import HWTimer
from shelley.shelleypy import operation, system, claim


# @claim("system check F (wait | END);")
@system(uses={})
class Timer:
    def __init__(self, period_ms=1000):
        self._timer = HWTimer()
        self.period_ms = period_ms

    @operation(initial=True, next=["cancel", "done"], check_return=True)
    async def start(self):
        # await asyncio.sleep_ms(self.period_ms)
        # concorrência aqui entre qlqr coisa e timer?!
        result = await self._timer.xx()
        if result == 0:
            return "cancel"
        else:
            return "done"

    @operation(final=True, next=["start"])
    async def cancel(self):
        self._timer.cancel()

    @operation(final=True, next=["start"])
    async def done(self):
        self._timer.done()
