from shelley.shelleypy import operation, system
from valve import Valve


@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, final=True, next=["run"])
    def run(self, time_ms=1000):
        self.a.open()
        self.b.open()
        delay(time_ms)
        self.a.close()
        self.b.close()
        return "run"

