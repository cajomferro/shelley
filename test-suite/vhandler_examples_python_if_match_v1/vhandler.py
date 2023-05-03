from valve import Valve
from led import LED
from shelley.shelleypy import operation, system, claim


@system(uses={"a": "Valve", "b": "Valve", "led": "LED"})
class App:
    def __init__(self):
        self.a = Valve()
        self.b = Valve()
        self.led = LED()

    @operation(initial=True, next=["try_open", "close_a", "close_b"])
    def try_open(self, use_a=True, blink_led=True):
        if use_a:
            match self.a.test():
                case "open":
                    self.a.open()
                    if blink_led:
                        for i in range(10):
                            self.led.on()
                            self.led.off()
                        return "close_a"
                    else:
                        return "close_a"
                case "clean":
                    self.a.clean()
                    return "try_open"
        else:
            match self.b.test():
                case "open":
                    self.b.open()
                    return "close_b"
                case "clean":
                    self.b.clean()
                    return "try_open"

    @operation(final=True, next=["try_open"])
    def close_a(self):
        self.a.close()
        return "try_open"

    @operation(final=True, next=["try_open"])
    def close_b(self):
        self.b.close()
        return "try_open"


    # @operation(initial=True, next=["try_open", "close_a", "close_b"])
    # def try_open(self, use_a=True, blink_led=True):
    #     if use_a:
    #         match self.a.test():
    #             case "open":
    #                 self.a.open()
    #                 # if blink_led:
    #                 #     for i in range(10):
    #                 #         self.led.on()
    #                 #         self.led.off()
    #                 return "close_a"
    #             case "clean":
    #                 self.a.clean()
    #                 return "try_open"
    #     else:
    #         return "try_open"

    # @operation(initial=True, next=["try_open", "close_a", "close_b"])
    # def try_open(self, use_a=True, blink_led=True):
    #     match self.a.test():
    #         case "open":
    #             self.a.open()
    #             # if blink_led:
    #             #     for i in range(10):
    #             #         self.led.on()
    #             #         self.led.off()
    #             return "close_a"
    #         case "clean":
    #             self.a.clean()
    #             return "try_open"
    #     # match self.b.test():
    #     #     case "open":
    #     #         self.b.open()
    #     #         if blink_led:
    #     #             for i in range(10):
    #     #                 self.led.on()
    #     #                 self.led.off()
    #     #         return "close_b"
    #     #     case "clean":
    #     #         self.b.clean()
    #     #         return "try_open"