from shelley.shelleypy import operation, system, claim
from hw import HWValve
from shelley.shelleypy import operation, system, claim


@system(uses={})
class Valve:
    def __init__(self, port):
        self._valve = HWValve(port)

    @operation(initial=True, next=["ready", "error"])
    async def status(self):
        if self._valve.ready():
            return "ready"
        else:
            return "error"

        # return True --> THIS IS INVALID HERE

    @operation(next=["on", "off"])
    async def ready(self):
        print("Valve is ready!")

    @operation(next=["clean"])
    async def error(self):
        print("Valve is stuck! Please clean it.")

    @operation(final=True, next=["status"])
    async def clean(self):
        print("Cleaning now...")
        self._valve.clean()

    @operation(next=["off"])
    async def on(self):
        self._valve.open()

    @operation(final=True, next=["status"])
    async def off(self):
        self._valve.close()
