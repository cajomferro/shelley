from .controller import Controller
from shelley.shelleypy import (
    operation,
    system,
    claim,
)


@system(uses={"c1": "Controller"})  # , "c2": "Controller"})
class App:
    def __init__(self):
        self.c1 = Controller()

    @operation(initial=True, final=True, next=[])
    async def main(self):
        await self.c1.click1()
        await self.c1.click2()
        return ""
