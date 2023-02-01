from valve import Valve
from shelley.shelleypy import operation, system, claim


@system(uses={"a": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()

    @operation(initial=True, final=True, next=["main"])
    def main(self):
        match self.a.test():
            case "open":
                self.a.open()
                self.a.close()
                return "main"
            case "clean":
                self.a.clean()
                return "main"
