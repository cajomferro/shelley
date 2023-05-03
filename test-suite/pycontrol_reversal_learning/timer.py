from shelley.shelleypy import operation, system, claim
import machine

@system(uses={})
class Timer:
    def __init__(self, period_ms=1000):
        self.period_ms = period_ms

    @op_initial_final
    def wait(self):
        machine.sleep_ms(self.period_ms)
        return "wait"
