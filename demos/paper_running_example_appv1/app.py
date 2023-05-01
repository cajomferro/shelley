from valve import Valve
from shelley.shelleypy import system, operation, claim, op_initial_final


@claim("integration check (!b.open) W a.open;")
@system(uses={"a": "Valve", "b": "Valve"})
class AppV1:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @op_initial_final
    def main(self):
        match self.a.test():
            case "open":
                self.a.open()
                match self.b.test():
                    case "open":
                        self.b.open()
                        self.a.close()
                        self.b.close()
                        return ""
                    case "clean":
                        self.b.clean()
                        self.a.close()
                        print("Failed to open valves")
                        return ""
            case "clean":
                self.a.clean()
                print("Failed to open valves")
                return ""

    # uncomment for requirement error
    # @op_initial_final
    # def main(self):
    #     match self.b.test():
    #         case "open":
    #             self.b.open()
    #             match self.a.test():
    #                 case "open":
    #                     self.a.open()
    #                     self.b.close()
    #                     self.a.close()
    #                     return ""
    #                 case "clean":
    #                     self.a.clean()
    #                     self.b.close()
    #                     print("Failed to open valves")
    #                     return ""
    #         case "clean":
    #             self.b.clean()
    #             print("Failed to open valves")
    #             return ""