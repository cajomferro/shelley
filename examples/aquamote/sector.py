from .valve import Valve
from shelley.shelleypy import system, claim, op, op_initial, op_initial_final, op_final

@claim("system check F try_open;")
@claim("integration check (!b.open) W a.open;")
@claim("subsystem b check G (open -> X close);")
@system(uses={"a": "Valve", "b": "Valve"})
class Sector:

    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @op_initial
    def try_open(self):
        match self.a.test():
            case "open":
                self.a.open()
                match self.b.test():
                    case "open":
                        self.b.open()
                        return "ok"
                    case "clean":
                        self.b.clean()
                        self.a.close()
                        return "fail"
            case "clean":
                self.a.clean()
                return "fail"

    @op_final
    def fail(self):
        print("Failed to open valves")
        return "try_open"

    @op
    def ok(self):
        return "close"

    @op_final
    def close(self):
        self.a.close()
        self.b.close()
        return "try_open"
