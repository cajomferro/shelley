from valve import Valve
from shelley.shelleypy import operation, system, claim


@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, final=True, next=["main"])
    def main(self, use_a=True):
        if use_a:
            self.a.open()
            self.a.close()
            return "main"
        else:
            self.b.open()
            self.b.close()
            return "main"