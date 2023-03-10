from shelley.shelleypy import system, claim, op, op_initial, op_initial_final, op_final
import machine

@system(uses={})
class Timer:
    def __init__(self, period_ms=1000):
        self.period_ms = period_ms

    @op_initial_final
    def wait(self):
        machine.sleep_ms(self.period_ms)
        return "wait"
