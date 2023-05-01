from .controller import Controller
from shelley.shelleypy import system, operation, claim, op_initial_final


# REQ1
@claim("integration check G (c.boot -> F (c.sleep & END));")
@system(uses={"c": "Controller"})
class App:
    def __init__(self):
        self.c = Controller()

    @op_initial_final
    def run(self, max_tries=3):
        self.c.boot()

        for _ in range(max_tries):
            match self.c.try_update():
                case "follow_plan_online":
                    self.c.follow_plan_online()
                    self.c.sleep()  # Omit this for integration error
                    return ["run"]
                case "follow_plan_offline":
                    self.c.follow_plan_offline()
                    self.c.sleep()
                    return ["run"]
                case "try_update_error":
                    self.c.try_update_error()
        else: # omit this for integration error
            self.c.follow_plan_offline()


        self.c.sleep()
        return ["run"]


