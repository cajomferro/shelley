from timer import Timer
from power import Power
from wireless import Wireless
from sector import Sector
from req_parser import RequestParser

from shelley.shelleypy import system, claim, op, op_initial, op_initial_final, op_final


# shelleypy controller.py  -o controller.shy && shelleymc -u uses.yml -s controller_extended.shy

# @claim("system check (boot & F (sleep & END));")
# claim9: if update fails we must run the sequential plan and never the parallel plan until sleeping
@claim("system check G (update_failed_last_try -> (F sequential_plan));") # same as below
@claim("system check G (update_failed_last_try -> ((!parallel_plan) U sleep));") # same as below
@claim("integration check G (this.update_failed_last_try -> ((F this.sequential_plan) & ((!this.parallel_plan) U (w.start | END))));")
#
# @claim("integration check G ((w.start_ok & F w.stop) -> X w.request);")
# @claim(
#     "integration check G ((pw.wake_up & (X (!w.start))) -> (!(F (vh.sec1)) & !(F (vh.sec2))));"
# )
# forcing wireless before sleeping
#@claim("integration check (!this.sleep) W w.start;")
#
# claim1: not possible to run the parallel plan unless you try to connect first [activate this if you want to be more restrictive]
@claim("integration check (!this.parallel_plan) W w.stop;")
#
# claim3: if not dry-run, at least sector one must be tried to run before sleeping
@claim("integration check G (w.start -> ((!this.sleep) W sec1.try_open));")  # change to sector2 for error
#
# claim4: unsuccessfully connecting to server implies try running the sequential plan
@claim("integration check G ((w.start & !(F w.request_ok)) -> ((F this.sequential_plan)));")  # change to sector2 for error
# WARNING: this claim is already covered by claim9 hence it is not possible to find a counterexample (skipping on thesis)
#
# claim5: sucessfully connecting to server and receiving the parallel request implies running the parallel plan
@claim(
    "integration check G ((w.start & !(F w.request_error) & (F w.request_ok) & (F this.parallel_plan)) -> ((F sec2.try_open) ));")
#
# claim2: sector1 must always precede sector2
@claim("integration check (!sec2.try_open) W sec1.try_open;")  # change order for error
#
# claim7: Make sure we always wait in between turning on and off sectors and we eventually close the sector after open
@claim(
    "integration check G ((sec1.ok -> F (t.wait & (F (sec1.close)))) & (sec2.ok -> X (t.wait & (X (sec2.close)))));")
#
# claim6: Same as before, but more specific to sequential plan (skipping this in the thesis)
# @claim(
#    "integration check G (this.sequential_plan -> ((sec1.ok -> X (t.wait & (X (sec1.close)))) & (sec2.ok -> X (t.wait & (X (sec2.close))))) U this.sleep);")
# #
# claim8: Make sure that the sequential plan does not open both valves at the same time
# @claim("integration check G (sec1.ok -> ((! sec2.try_open) U sec1.close) & (sec2.ok -> ((! sec1.try_open)) U sec2.close));") # THIS MUST FAIL for the parallel 
# @claim("integration check G (w.start -> (sec1.ok -> ((! sec2.try_open) U sec1.close) & (sec2.ok -> ((! sec1.try_open)) U sec2.close)));") # Why is this true? I think it is beccaue we have a w.start -> and then we don't have X, nor F, nor U
@claim(
    "integration check G (this.sequential_plan -> (sec1.ok -> ((! sec2.try_open) U sec1.close) & (sec2.ok -> ((! sec1.try_open)) U sec2.close)) U this.sleep);")
@claim(
    "integration check G (this.sequential_plan -> (sec1.try_open -> ((! sec2.try_open) U (sec1.close | sec1.fail)) & (sec2.try_open -> ((! sec1.try_open)) U (sec2.close | sec2.fail))) U this.sleep);")
#
@system(uses={"t": "Timer", "sec1": "Sector", "sec2": "Sector", "w": "Wireless"})
class Controller:
    def __init__(self):
        self.t = Timer()
        self.w = Wireless()
        self.sec1 = Sector()  # controls 2 valves
        self.sec2 = Sector()  # controls 2 valves

    @op_initial
    def try_update(self):
        match self.w.start():
            case "start_ok":
                self.w.start_ok()
                match self.w.request("hello"):
                    case "request_ok":
                        _, self._plan_type = self.w.request_ok()
                        self.w.stop()
                        return "update_ok"
                    case "request_error":
                        self.w.request_error()
            case "start_failed":
                self.w.start_failed()

        self.w.stop()
        return "update_failed"

    @op
    def update_failed(self):
        return ["try_update", "update_failed_last_try"]

    @op
    def update_failed_last_try(self):
        return ["sequential_plan"]

    @op
    def update_ok(self):
        if self._plan_type == "sequential":
            return "sequential_plan"
        elif self._plan_type == "parallel":
            return "parallel_plan"
        else:
            return "parallel_plan"

    @op_initial
    def sequential_plan(self):
        match self.sec1.try_open():
            case "ok":
                self.sec1.ok()
                self.t.wait()
                self.sec1.close()
                match self.sec2.try_open():
                    case "ok":
                        self.sec2.ok()
                        self.t.wait()
                        self.sec2.close()
                    case "fail":
                        self.sec2.fail()
            case "fail":
                self.sec1.fail()

        return "sleep"

    @op
    def parallel_plan(self):
        match self.sec1.try_open():
            case "ok":
                self.sec1.ok()
                match self.sec2.try_open():
                    case "ok":
                        self.sec2.ok()
                        self.t.wait()
                        self.sec2.close()
                        self.sec1.close()
                    case "fail":
                        self.sec2.fail()
                        self.t.wait()
                        self.sec1.close()
            case "fail":
                self.sec1.fail()
                match self.sec2.try_open():
                    case "ok":
                        self.sec2.ok()
                        self.t.wait()  # comment for error
                        self.sec2.close()
                    case "fail":
                        self.sec2.fail()

        return "sleep"

    @op_initial_final
    def sleep(self):
        # TODO: call internal hw function to sleep
        return ["try_update", "sequential_plan"]
