from .valve import Valve
from .timer import Timer
from shelley.shelleypy import operation, system, claim, op_initial_final


@claim("system check F sector1 | F sector2 | F sector3 | F sector4 ;")
@claim(
    "integration check G ((v1.on -> X (t.wait & (X (v1.off)))) & (v2.on -> X (t.wait & (X (v2.off)))) & (v3.on -> X (t.wait & (X (v3.off)))) & (v4.on -> X (t.wait & (X (v4.off)))));"
)
@system(uses={"v1": "Valve", "v2": "Valve", "v3": "Valve", "v4": "Valve", "t": "Timer"})
class Sectors:
    def __init__(self):
        self.v1 = Valve()
        self.v2 = Valve()
        self.v3 = Valve()
        self.v4 = Valve()
        self.t = Timer()

    @op_initial_final
    def sector1(self):
        self.v1.on()
        self.t.wait()
        self.v1.off()
        return ["sector1", "sector2", "sector3", "sector4"]

    @op_initial_final
    def sector2(self):
        self.v2.on()
        self.t.wait()
        self.v2.off()
        return ["sector1", "sector2", "sector3", "sector4"]

    @op_initial_final
    def sector3(self):
        self.v3.on()
        self.t.wait()
        self.v3.off()
        return ["sector1", "sector2", "sector3", "sector4"]

    @op_initial_final
    def sector4(self):
        self.v4.on()
        self.t.wait()
        self.v4.off()
        return ["sector1", "sector2", "sector3", "sector4"]
