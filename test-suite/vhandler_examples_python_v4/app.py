from .controller import Controller
from shelley.shelleypy import operation, system, claim


@claim("system check G (run -> F (run & END));")
@system(uses={"c": "Controller"})
class App:
    def __init__(self):
        self.c = Controller()

    @operation(initial=True, final=True, next=[])
    async def run(self, both_sectors: bool = True):
        match await self.c.sector1_try():
            case "run1":
                await self.c.run1()
                if both_sectors is True:
                    await self.c.sector2()
                    return ""
                else:
                    await self.c.close1()
                    return ""
            case "error1":
                await self.c.error1()
                return ""

