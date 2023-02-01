from valve import Valve
from shelley.shelleypy import operation, system, claim


@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["close_a", "close_b"])
    def open_all(self, use_a=True):
        if use_a:
            self.a.open()
        else:
            self.b.open()
            return "close_b"

        return "close_a"
    @operation(final=True, next=["open_all"])
    def close_a(self):
        self.a.close()
        return "open_all"

    @operation(final=True, next=["open_all"])
    def close_b(self):
        self.b.close()
        return "open_all"