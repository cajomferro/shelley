from shelley.shelleypy import operation, system, claim
import machine

@system(uses={})
class Power:
    @op_initial
    def wake_up(self):
        machine.wake_up()
        return ["sleep"]

    @op_final
    def sleep(self):
        machine.ready_to_sleep()
        return ["wake_up"]