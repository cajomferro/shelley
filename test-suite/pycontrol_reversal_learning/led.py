from shelley.shelleypy import operation, system, claim

@system(uses={})
class LED:
    def __init__(self, hw_bind):
        self._led = hw_bind

    @op_initial
    def on(self):
        self._led.on()
        return "off"

    @op_final
    def off(self):
        self._led.off()
        return "on"

