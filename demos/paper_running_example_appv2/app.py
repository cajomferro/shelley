from sector import Sector
from shelley.shelleypy import system, operation, claim, op_initial_final


@system(uses={"s": "Sector"})
class AppV2:
    def __init__(self):
        self.s = Sector()

    @op_initial_final
    def main(self):
        match self.s.try_open():
            case "close":
                self.s.close()
                return ""
            case "fail":
                self.s.fail()
                return ""
