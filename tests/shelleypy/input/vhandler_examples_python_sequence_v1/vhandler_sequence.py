from valve import Valve
from shelley.shelleypy import operation, system, claim


@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["close_valves"])
    def open_valves(self):
        self.a.open()
        self.b.open()
        return "close_valves"

    @operation(final=True, next=["open_valves"])
    def close_valves(self):
        self.a.close()
        self.b.close()
        return "open_valves"


