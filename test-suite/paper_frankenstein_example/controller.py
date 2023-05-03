from .valve import Valve
from .timer import Timer
from shelley.shelleypy import (
    operation,
    system,
    claim,
)


@claim("system check G (level1 -> X (standby1 | (level2 & X standby2) | END));")
@claim("integration check G (a.on -> (X t.start & F (t.done & F a.off)));")
@system(uses={"a": "Valve", "b": "Valve", "t": "Timer"})
class Controller:

    def __init__(self, valve_a_first_off: bool = True):
        self.a = Valve()
        self.b = Valve()
        self.t = Timer()

    @operation(initial=True, next=["standby1", "level2"])
    async def level1(self):
        await self.a.on()
        match await self.t.start():
            case "done":
                return "standby1"
            case "cancel":
                return "level2"

    @operation(next=["standby2"])
    async def level2(self):
        await self.t.cancel()
        await self.b.on()
        match await self.t.start():
            case "done":
                return "standby2"
            case "cancel":
                return "standby2"

    @operation(final=True, next=["level1"])
    async def standby1(self):
        await self.t.done()
        await self.a.off()
        return "level1"

    @operation(final=True, next=["level1"])
    async def standby2(self, valve_a_first: bool = True):
        await self.t.done()
        if valve_a_first is True:
            await self.a.off()
            await self.b.off()
            return "level1"
        else:
            await self.b.off()
            await self.a.off()
            return "level1"

#
#	# after level1, eventually we have standby1 or standby2
#	system check G (level1 -> F (standby1 | standby2));
#
#	# after level2, eventually we have standby2
#	system check G (level2 -> F standby2);
#
#	# immediately after level2, we must have standby2
#	system check G (level2 -> X standby2);
#
#	# immediately after level2, we cannot observe standby1
#	system check G (level2 -> ! X standby1);
#
#	# immediately after standby1, we cannot observe level2
#	system check G (standby1 -> ! X level2);
#
#	# if valve a is turned on the timer must timedone eventually
#    integration check G (a.on -> F t.done);
#
#	# valve a is turned on and the timer either is canceled or timeout
#    # integration check G (a.on -> F (t.cancel | t.done)); # THIS IS REDUNDANT
#
#    #integration check G (a.on -> F t.cancel); # THIS IS FALSE
#
#	# valve a is turned on and either timer timeout or valve b is turned on
#    integration check F (a.on & F (t.done | b.on) );
#
#	# t.cancel and t.done cannot immediately succeed a.on
#    # integration check F (a.on & ! X (t.cancel | t.done)); # this doesn't make sense because there is a TRUE & FALSE
#
#    integration check G (b.on -> ! X (a.on));
#
#    integration check a.on;
