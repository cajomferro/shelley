from valve import Valve
from shelley.shelleypy import system, operation, claim, op_initial, op_final


@claim("integration check (!b.open) W a.open;")
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
                        return "close"
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

    @op_final
    def close(self):
        self.a.close()
        self.b.close()
        return "try_open"
