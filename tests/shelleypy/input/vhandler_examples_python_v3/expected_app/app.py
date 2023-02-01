from .controller import Controller
from shelley.shelleypy import system, operation, claim

#@claim("system check F (run & END);")
@claim("integration check G (c.boot -> F (c.sleep & END));")
@system(uses={"c": "Controller"})
class App:
    def __init__(self):
        self.c = Controller()

    @operation(initial=True, final=True, next=[])
    def run(self, dry_run=False):
        self.c.boot()
        if dry_run:
            self.c.sleep()
        else:
            for _ in range(3):
                match self.c.try_update():
                    case "follow_plan_online":
                        self.c.follow_plan_online()
                        self.c.sleep()
                        return
                    case "follow_plan_offline":
                        self.c.follow_plan_offline()
                        self.c.sleep() # Omit this for integration error
                        return
                    case "try_update":
                        pass
            else:
                self.c.follow_plan_offline()
                self.c.sleep()
                return
