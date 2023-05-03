from valve import Valve
from shelley.shelleypy import operation, system, claim


@claim("integration check (! b.open) W a.open;")
@system(uses={"a": "Valve", "b": "Valve"})
class AppV1:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()

    @operation(initial=True, final=True, next=[])
    def run(self):
        match self.a.test():
            case "open":
                self.a.open()
                match self.b.test():
                    case Valve.open:
                        self.b.open()
                        self.a.close()
                        self.b.close()
                        return ""
                    case "clean":
                        self.b.clean()
                        self.a.close()
            case "clean":
                self.a.clean()
        print("Failed to open valves")
        return AppV1.run

        # for _ in range(3):
        #     match self.a.test():
        #         case "open":
        #             self.a.open()
        #             for _ in range(3):
        #                 match self.b.test():
        #                     case "open":
        #                         self.b.open()
        #                         self.a.close()
        #                         self.b.close()
        #                         return ""
        #                     case "clean":
        #                         self.b.clean()
        #                         self.a.close()
        #                         print("Failed to open valves")
        #         case "clean":
        #             self.a.clean()
        #             print("Failed to open valves")
        # return ""

    #   match self.b.test():
    #     case "open":
    #       self.b.open()
    #       match self.a.test():
    #         case "open":
    #           self.a.open()
    #           # Handle open valves...
    #           self.b.close(); self.a.close()
    #           return ""
    #         case "clean":
    #           self.a.clean(); self.b.close()
    #           print("Failed to open valves")
    #           return ""
    #     case "clean":
    #       self.b.clean()
    #       print("Failed to open valves")
    #       return ""
