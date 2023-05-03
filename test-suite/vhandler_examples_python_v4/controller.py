from .valve import Valve
from .timer import Timer
from .led import LED
from shelley.shelleypy import operation, system, claim


@claim("integration check G ( (va.on -> F(t.wait & F va.off)) & (vb.on -> F(t.wait & F vb.off)));")
@claim("subsystem va check G (on -> X off);")
@claim("subsystem t check F wait;")
@system(uses={"va": "Valve", "vb": "Valve", "t": "Timer", "l": "LED"})
class Controller:
    VALVE_A_FIRST_OFF: bool

    def __init__(self, valve_a_first_off: bool = True):
        self.va = Valve()
        self.vb = Valve()
        self.t = Timer()
        self.l = LED()
        self.VALVE_A_FIRST_OFF = valve_a_first_off

    @operation(initial=True, next=["run1", "error1"])
    async def sector1_try(self):
        await self.l.on()
        match await self.va.status():
            case "ready":
                return "run1"
            case "error":
                return "error1"

    @operation(next=["close1", "sector2"])
    async def run1(self):
        """
        # va.ready is not a callback! it is just an extra step to print a message based on the previous return
        """
        await self.va.ready()
        await self.va.on()
        return ["close1", "sector2"]

    @operation(final=True, next=["sector1_try"])
    async def error1(self):
        """
        # va.error is not a callback! it is just an extra step to print a message based on the previous return
        """
        await self.l.off()
        await self.va.error()
        await self.va.clean()
        return "sector1_try"

    @operation(final=True, next=["sector1_try"])
    async def close1(self):
        await self.t.wait()
        await self.va.off()
        await self.l.off()
        return "sector1_try"

    @operation(final=True, next=["sector1_try"])
    async def sector2(self):
        match await self.vb.status():
            case "ready":
                await self.vb.ready()
                await self.vb.on()
                await self.t.wait()
                if self.VALVE_A_FIRST_OFF is True:
                    await self.va.off()
                    await self.vb.off()
                    await self.l.off()
                    return "sector1_try"
                else:
                    await self.vb.off()
                    await self.va.off()
                    await self.l.off()
                    return "sector1_try"
            case "error":
                await self.vb.error()
                await self.vb.clean()
                await self.t.wait()
                await self.va.off()
                await self.l.off()
                return "sector1_try"
