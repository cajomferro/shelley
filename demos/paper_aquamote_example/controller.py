from .sectors import Sectors
from .power import Power
from .wireless import Wireless

from shelley.shelleypy import system, claim, op, op_initial, op_final

# REQ1
# not possible to run any plan unless you try to connect and disconnect first
@claim("integration check (!s.sector1) W w.stop;")

# REQ2
# sector1 must always precede sector2
@claim("integration check (!s.sector2) W s.sector1;")

# REQ3
# if not dry-run, at least sector one must run before sleeping
@claim(
    "integration check G (w.start -> ((!pw.sleep) W s.sector1));"
)

# REQ4
# unsucessfully connecting to server implies running the winter plan
@claim(
    "integration check G ((w.start & !(F w.request_ok)) -> ((F (s.sector1 & X(!s.sector2)))));"
)

# REQ5
# sucessfully connecting to server implies running the summer plan
@claim(
    "integration check G ((w.start & !(F w.request_error) & (F w.request_ok)) -> ((F (s.sector1 & (F (s.sector2 | END)))) ));"
)

@system(uses={"s": "Sectors", "pw": "Power", "w": "Wireless"})
class Controller:
    def __init__(self):
        self.s = Sectors()
        self.pw = Power()
        self.w = Wireless()

    @op_initial
    def boot(self):
        self.pw.wake_up()
        return ["try_update", "sleep"]

    @op
    def try_update(self):
        match self.w.start():
            case "start_ok":
                self.w.start_ok()
                match self.w.request("hello"):
                    case "request_ok":
                        self.w.request_ok()
                        self.w.stop()
                        return ["follow_plan_online"]
                    case "request_error":
                        self.w.request_error()
                        self.w.stop()
                        return ["follow_plan_offline"]
            case "start_failed":
                self.w.start_failed()
                self.w.stop()
                return ["try_update_error"]

    @op
    def try_update_error(self):
        return ["try_update, follow_plan_offline"]

    @op
    def follow_plan_online(self):
        self.s.sector1()
        self.s.sector2()
        return ["sleep"]

    @op
    def follow_plan_offline(self):
        self.s.sector1()
        return ["sleep"]

    @op_final
    def sleep(self):
        self.pw.sleep()
        return ["boot"]
