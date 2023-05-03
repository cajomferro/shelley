from shelley.shelleypy import operation, system, claim

@system(uses={})
class SOL:
    def __init__(self, hw_bind):
        self._sol = hw_bind

    @op_initial
    def on(self):
        self._sol.on()
        return "off"

    @op_final
    def off(self):
        self._sol.off()
        return "on"

