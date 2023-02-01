from .valve import Valve
from shelley.shelleypy import operation, system, claim


@claim("integration check (!b.open) W a.open;")  # equivalent to: ((! b.open) U a.open) | (G (! b.open))
@claim("subsystem b check G (open -> X close);")  # equivalent to: ((! b.open) U a.open) | (G (! b.open))
@system(uses={"a": "Valve", "b": "Valve"})
class ValveHandler:

    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, next=["close", "close_all", "fail"])
    def try_open(self, fallback_b_valve=True):
        match self.a.test():
            case "open":
                self.a.open()
                print("Valve a opened!")
                if fallback_b_valve:
                    match self.b.test():
                        case "open":
                            self.b.open()
                            return "close_all"
                        case "clean":
                            self.b.clean()
                            return "close"
                else:
                    return "close"
            case "clean":
                self.a.clean()
                return "fail"  # Interesting to note that returning here the "close" method instead raises an integration error (a.test -> a.clean -> a.close)

    @operation(final=True, next=["try_open"])
    def fail(self):
        print("Valve a failed!")
        return "try_open"

    @operation(final=True, next=["try_open"])
    def close(self):
        self.a.close()  # comment for faulty controller
        print("Valve a closed!")
        return "try_open"

    @operation(final=True, next=["try_open"])
    def close_all(self):
        self.a.close()
        self.b.close()
        return "try_open"
