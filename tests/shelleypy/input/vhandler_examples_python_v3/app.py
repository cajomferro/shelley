from .controller import Controller
from shelley.shelleypy import (
    operation,
    system,
    claim,
)

@claim("system check G (main -> F (main & END));")
@system(uses={"c1": "Controller", "c2": "Controller"})
class App:
    def __init__(self):
        self.c1 = Controller()
        self.c2 = Controller()

    @operation(initial=True, final=True, next=[])
    def main(self, both_sectors: bool = True):
        match self.c1.step1_test():
            case "step1_start":
                self.c1.step1_start()
                if both_sectors is True:
                    self.c1.step2()
                    return ""
                else:
                    self.c1.step1_stop()
                    return ""
            case "step1_handle_error":
                self.c1.step1_handle_error()
                match self.c2.step1_test():
                    case "step1_start":
                        self.c2.step1_start()
                        self.c2.step1_stop()
                        return ""
                    case "step1_handle_error":
                        self.c2.step1_handle_error()
                        return ""

