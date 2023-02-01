from .valve import Valve
from .timer import Timer
from shelley.shelleypy import (
    operation,
    system,
    claim,
)

#@claim("system check G (step1_test -> F ((step1_handle_error & END) | (step1_stop & END) | (step2 & END)));") # R1
@claim("integration check G ( (va.open -> F(t.wait & F va.close)) & (vb.open -> F(t.wait & F vb.close)));") # R2
@claim("subsystem va check G (test -> X !test);") # R3
@system(uses={"va": "Valve", "vb": "Valve", "t": "Timer"})
class ControllerAlt:

    def __init__(self, valve_a_first_off: bool = True):
        self.va = Valve()
        self.vb = Valve()
        self.t = Timer()

    @operation(initial=True, final=True, next=["run"])
    def run(self, both_sectors: bool = True, valve_a_first: bool = True):
        match self.va.test():
            case "open":
                self.va.open() # step1_start
                if both_sectors is True: # step2
                    match self.vb.test():
                        case "open":
                            self.vb.open()
                            self.t.wait()
                            if valve_a_first is True:
                                self.va.close()
                                self.vb.close()
                                return "run"
                            else:
                                self.vb.close()
                                self.va.close()
                                return "run"
                        case "clean":
                            self.vb.clean()
                            self.t.wait()  # wait for va to irrigate
                            self.va.close() # omitting va.close here yields an integration error
                            return "run"
                        case "test":
                            self.t.wait()  # wait for va to irrigate
                            self.va.close()  # omitting va.close here yields an integration error
                            return "run"
                else: # step1_stop
                    # switching the order of these calls violates R2
                    self.t.wait()
                    self.va.close()
                    return "run"

            case "clean": # step1_handle_error
                self.va.clean()
                return "run"
            case "test":
                self.va.clean()  # omitting va.clean here violates R3
                return "run"