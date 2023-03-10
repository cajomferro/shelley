from controller import Controller
from timer import Timer

from shelley.shelleypy import system, claim, op, op_initial, op_initial_final, op_final


# @claim("system check F (run & END);")
@claim("integration check F c.sequential_plan | F c.parallel_plan;")
@claim("integration check F (c.sleep & END);")
@claim("integration check F c.try_update;")
@system(uses={"c": "Controller", "t": "Timer"})
class App:
    def __init__(self):
        self.c = Controller()
        self.t = Timer()

    @op_initial_final
    def run(self):

        # Alternative that doesn't assume the loop runs at least once
        match self.c.try_update():
            case "update_ok":
                match self.c.update_ok():
                    case "sequential_plan":
                        self.c.sequential_plan()
                    case "parallel_plan":
                        self.c.parallel_plan()
                self.c.sleep()
                return ""
            case "update_failed":
                self.c.update_failed()
                self.t.wait()

        for _ in range(2):
            match self.c.try_update():
                case "update_ok":
                    match self.c.update_ok():
                        case "sequential_plan":
                            self.c.sequential_plan()
                        case "parallel_plan":
                            self.c.parallel_plan()
                    self.c.sleep()
                    return ""
                case "update_failed":
                    self.c.update_failed()
                    self.t.wait()

        self.c.update_failed_last_try()
        self.c.sequential_plan()
        self.c.sleep()
        return ""

        # for _ in range(3):
        #     match self.c.try_update():
        #         case "sleep":
        #             self.c.sleep()
        #             return ""
        #         case "update_failed":
        #             self.c.update_failed()
        # else:
        #     self.c.update_failed_last_try()
        #     self.c.sleep()
        # return ""
