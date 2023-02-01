from valve import Valve
from shelley.shelleypy import operation, system, claim

# shelleypy loop_v1.py  -o loop_v1.shy

@system(uses={"v1": "Valve"})
class VHandler:
    def __init__(self):
        self.v1 = Valve()

    @operation(initial=True, next=["all_tries_failed", "close"])
    def main(self, mytest=False):
        self.v1.init()
        for _ in range(10):
            match self.v1.test():
                case "ok":
                    self.v1.ok()
                    if mytest:
                        self.v1.on()
                    return "close"
                case "error":
                    self.v1.error()
        self.v1.clean()
        return "all_tries_failed"

    @operation(final=True, next=[""])
    def all_tries_failed(self):
        return ""


    @operation(final=True, next=[""])
    def close(self):
        self.v1.off()
        return ""

