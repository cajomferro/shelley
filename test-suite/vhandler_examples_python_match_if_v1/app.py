from .vhandler import ValveHandler
from shelley.shelleypy import operation, system, claim


@system(uses={"vh": "ValveHandler"})
class AppV2:

    def __init__(self):
        self.vh = ValveHandler()

    @operation(initial=True, final=True, next=[])
    def main(self):
        match self.vh.try_open():
            case "close":
                self.vh.close()
                return ""
            case "fail":
                self.vh.fail()
                return ""

