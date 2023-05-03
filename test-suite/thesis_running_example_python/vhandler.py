from .valve import Valve
from shelley.shelleypy import operation, system, claim

@claim("system check F try_open;")
@claim("integration check (!b.open) W a.open;")  # equivalent to: ((! b.open) U a.open) | (G (! b.open))
@claim("subsystem b check G (open -> X close);")
@system(uses={"a": "Valve", "b": "Valve"})
class ValveHandler:

    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["close", "fail"])
    def try_open(self):
        match self.a.test():
            case "open":
                self.a.open()
                match self.b.test():
                    case "open":
                        self.b.open()
                        return "close"
                    case "clean":
                        self.b.clean()
                        self.a.close() # comment for faulty controller
                        return "fail"
            case "clean":
                self.a.clean()
                return "fail"

    @operation(final=True, next=["try_open"])
    def fail(self):
        print("Failed to open valves")
        return "try_open"

    @operation(final=True, next=["try_open"])
    def close(self):
        self.a.close()
        self.b.close()
        return "try_open"
