from valve import Valve
from shelley.shelleypy import op_initial_final, op_final, op_initial, op, system, claim


@claim("integration check (! b.open) W a.open;")
@system(uses={"a": "Valve", "b": "Valve"})
class Sector:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @op_initial
    def open_a(self):
        match self.a.test():
            case "open":
                self.a.open()
                return ["close_a", "open_b"]
            case "clean":
                return "clean_a"

    @op_final
    def clean_a(self):
        self.a.clean()
        print("Failed to open valve a")
        return "open_a"

    @op_final
    def close_a(self):
        self.a.close()
        return "open_a"

    @op_final
    def open_b(self):
        match self.b.test():
            case "open":
                self.b.open()
                self.a.close()
                self.b.close()
                return ""
            case "clean":
                self.b.clean()
                self.a.close()
                return ""
