from .vhandler import ValveHandler
from shelley.shelleypy import operation, system, claim

@claim("subsystem vh check F try_open;")
@system(uses={"vh": "ValveHandler"})
class App:

    def __init__(self):
        self.vh = ValveHandler()

    @operation(initial=True, final=True, next=[])
    def main(self, dry_run=False):
        match self.vh.try_open():
            case "close":
                self.vh.close()
                return ""
            case "fail":
                self.vh.fail()

        for i in range(10):
            match self.vh.try_open():
                case "close":
                    self.vh.close()
                    return ""
                case "fail":
                    self.vh.fail()

        print("failed after all attempts")
        return ""

        # TODO: this has the problem with empty strings in LTL
        # if not dry_run:
        #     # match self.vh.try_open():
        #     #     case "close_all":
        #     #         self.vh.close_all()
        #     #         return ""
        #     #     case "fail":
        #     #         self.vh.fail()
        #     #         return ""
        #
        #     for i in range(10):
        #         match self.vh.try_open():
        #             case "close_all":
        #                 self.vh.close_all()
        #                 return ""
        #             case "fail":
        #                 self.vh.fail()
        #                 #return ""
        #
        #     print("failed after all attempts")
        # return ""

