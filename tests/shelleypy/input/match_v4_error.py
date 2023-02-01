from valve import Valve
from shelley.shelleypy import operation, system, claim

# shelleypy match_v4.py  -o match_v4.shy

@system(uses={"v1": "Valve"})
class VHandler:
    def __init__(self):
        self.v1 = Valve()

    @operation(initial=True, next=["close", "error"])
    def main(self):
        self.v1.init()
        match self.v1.test():
            case "ok":
                self.v1.ok()
                self.v1.on()
                return "close"
            case "error":
                self.v1.error()
                return "error"
        self.v1.cenas()
#        return "error" ERROR MISSING RETURN HERE

    @operation(final=True, next=[""])
    def error(self):
        self.v1.clean()
        return ""


    @operation(final=True, next=[""])
    def close(self):
        self.v1.off()
        return ""

