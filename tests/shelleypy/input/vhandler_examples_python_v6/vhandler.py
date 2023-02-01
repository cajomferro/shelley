from shelley.shelleypy import operation, system
from valve import Valve


@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["close_all"])
    def open_all(self):
        self.a.open()
        self.b.open()
        return "close_all"

    @operation(final=True, next=["open_all"])
    def close_all(self):
        self.a.close()
        self.b.close()
        return "open_all"
