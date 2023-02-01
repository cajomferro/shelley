from valve import Valve
from shelley.shelleypy import operation, system, claim


@system(uses={"v1": "Valve", "v2": "Valve"})
class App:
    def __init__(self):
        self.v1 = Valve()
        self.v2 = Valve()

    @operation(initial=True, next=[])
    def main(self):
        match self.v1.test():
            case "ok":
                self.v1.ok()
                self.v1.on()
                return ""
            case "error":
                self.v1.error()
                self.v2.on()
                return ""
        self.v1.on()
        return ""

