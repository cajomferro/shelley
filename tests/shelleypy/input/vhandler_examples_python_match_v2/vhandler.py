from valve import Valve
from shelley.shelleypy import operation, system, claim


@system(uses={"a": "Valve", "b": "Valve"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["try_open", "when_a", "when_b"])
    def try_open(self):
        #for _ in range(10):
        match self.a.test():
            case "open":
                self.a.open()
                return "when_a"
            case "clean":
                self.a.clean()
                match self.b.test():
                    case "mamas":
                        self.b.mamas()
                    case "open":
                        self.b.open()
                        return "when_b"
                    case "clean":
                        self.b.clean()
                        return "try_open"
                self.a.cenas()
                #return "try_open"
            case "omg":
                self.a.omg()
        return "try_open"

    @operation(final=True, next=["try_open"])
    def when_a(self):
        self.a.close()
        return "try_open"

    @operation(final=True, next=["try_open"])
    def when_b(self):
        self.b.close()
        return "try_open"

