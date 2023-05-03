from led import LED
from sol import SOL
from shelley.shelleypy import operation, system, claim


@system(uses={"led": "LED", "sol": "SOL"})
class Poke:

    def __init__(self, hw_bind):
        self.led = LED(hw_bind.LED)
        self.sol = SOL(hw_bind.SOL)

    @op_initial
    def led_on(self):
        self.led.on()
        return "led_off"

    @op_final
    def led_off(self):
        self.led.off()
        return ["led_on", "sol_on"]

    @op_initial
    def sol_on(self):
        self.sol.on()
        return "sol_off"

    @op_final
    def sol_off(self):
        self.sol.off()
        return ["led_on", "sol_on"]
