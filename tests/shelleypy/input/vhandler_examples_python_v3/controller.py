from .valve import Valve
from .timer import Timer
from shelley.shelleypy import (
    operation,
    system,
    claim,
)
from .led import LED


@claim("system check G (step1_test -> F ((step1_handle_error & END) | (step1_stop & END) | (step2 & END)));")  # R1
@claim("integration check G ( (a.open -> F(t.wait & F a.close)) & (b.open -> F(t.wait & F b.close)));")  # R2
@claim("subsystem va check G (test -> X !test);")  # R3
# @claim("subsystem vb check G (error -> X clean);") # this is false!
@system(uses={"a": "Valve", "b": "Valve", "t": "Timer", "l": "LED"})
class Controller:

    def __init__(self, valve_a_first_off: bool = True):
        self.a = Valve()
        self.b = Valve()
        self.t = Timer()
        self.l = LED()

    @operation(initial=True, next=["step1_start", "step1_handle_error"])
    def step1_test(self):
        self.l.on()
        match self.a.test():
            case "open":
                self.a.open()
                return "step1_start"
            case "clean":
                self.a.clean()  # omitting va.clean here violates R3
                return "step1_handle_error"

    @operation(next=["step1_stop", "step2"])
    def step1_start(self):
        return ["step1_stop", "step2"]

    @operation(final=True, next=["step1_test"])
    def step1_handle_error(self):
        self.l.off()
        return "step1_test"

    @operation(final=True, next=["step1_test"])
    def step1_stop(self):
        # switching the order of these calls violates R2
        self.t.wait()
        self.a.close()
        self.l.off()
        return "step1_test"

    @operation(final=True, next=["step1_test"])
    def step2(self, valve_a_first: bool = True):
        match self.b.test():
            case "open":
                self.b.open()
                self.t.wait()
                if valve_a_first is True:
                    self.a.close()
                    self.b.close()
                    self.l.off()
                    return "step1_test"
                else:
                    self.b.close()
                    self.a.close()
                    self.l.off()
                    return "step1_test"
            case "clean":
                self.b.clean()
                self.t.wait()  # wait for va to irrigate
                self.a.close()  # omitting va.close here yields an integration error
                self.l.off()
                return "step1_test"
            case "test":
                self.t.wait()  # wait for va to irrigate
                self.a.close()  # omitting va.close here yields an integration error
                self.l.off()
                return "step1_test"
