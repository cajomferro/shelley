from valve import Valve
from shelley.shelleypy import op_initial_final, op_final, op_initial, op, system, claim


@system(uses={"s": "Sector"})
class App:
    def __init__(self):
        self.s = Sector()

    @op_initial_final
    def run(self):
        match self.s.open_a():
            case ["close_a", "open_b"]:
                # case ["close_a", "open_b"]:
                timer.wait()
                self.s.open_b()
                return ""
            case "clean_a":
                self.s.clean_a()
                timer.wait()

        for _ in range(3):
            match self.s.open_a():
                # case "close_a":
                # timer.wait()
                # self.s.close_a()
                # return ""
                case ["close_a", "open_b"]:
                    # case ["close_a", "open_b"]:
                    timer.wait()
                    self.s.open_b()
                    return ""
                case "clean_a":
                    self.s.clean_a()
                    timer.wait()
        return ""
