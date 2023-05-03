from .twovalves import TwoValves
from shelley.shelleypy import (
    operation,
    system,
    claim,
)


@claim("system check G (main -> F (main & END));")
@system(uses={"t": "TwoValves"})
class AppTwoValves:
    def __init__(self):
        self.t = TwoValves()

    @operation(initial=True, final=True, next=[])
    def main(self):
        self.t.run()
        return ""