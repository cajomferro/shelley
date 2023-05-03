from .valve import Valve
from .timer import Timer
from shelley.shelleypy import (
    operation,
    system,
    claim,
)


# @claim("system check G (step1_test -> F ((step1_handle_error & END) | (step1_stop & END) | (step2 & END)));") # R1
# @claim("integration check G ( (va.open -> F(t.wait & F va.close)) & (vb.open -> F(t.wait & F vb.close)));") # R2
# @claim("subsystem va check G (test -> X !test);") # R3
@system(uses={"va": "Valve", "vb": "Valve"})
class TwoValves:

    def __init__(self):
        self.va = Valve()
        self.vb = Valve()

    @operation(initial=True, final=True, next=["run"])
    def run(self, both_sectors: bool = True, valve_a_first: bool = True):
        match self.va.test():
            case "open":
                self.va.open()
                if both_sectors is True:
                    match self.vb.test():
                        case "open":
                            self.vb.open()
                            if valve_a_first is True:
                                self.va.close()
                                self.vb.close()
                                return "run"  # run1
                            else:
                                self.vb.close()
                                self.va.close()
                                return "run"  # run1
                        case "clean":
                            self.vb.clean()
                            self.va.close()
                            return "run"  # run2
                        case "test":
                            # in theory, I should do self.vb.test() which implies doing a match, but this is an infinite loop...
                            self.va.close()
                            return "run"  # run3
                else:
                    self.va.close()
                    return "run"  # run4
            case "clean":
                self.va.clean()
                return "run"  # run5
            case "test":
                # in theory, I should do self.va.test() which implies doing a match, but this is an infinite loop...
                return "run"  # run6
