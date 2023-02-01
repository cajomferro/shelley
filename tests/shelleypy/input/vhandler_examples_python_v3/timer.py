from shelley.shelleypy import operation, system, claim


@claim("system check F (wait | END);")
@system(uses={})
class Timer:
    def __init__(self, period_ms=1000):
        self.period_ms = period_ms

    @operation(initial=True, final=True, next=["wait"])
    def wait(self):
        delay(self.period_ms)
