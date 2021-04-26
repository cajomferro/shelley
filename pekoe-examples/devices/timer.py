from decorators import *
from devices import Device
from native.generic.timer import Timer as TimerNative


class TimerDevice(Device):
    STARTED = 0
    CANCELED = 1
    TIMEOUT = 2

    timer_native = None

    def __init__(self, driver_id: str, timer_native: TimerNative):
        Device.__init__(self, driver_id)
        self.timer_native = timer_native

    @action
    @raise_event(STARTED)
    def start(self, duration: int):
        self.timer_native.attach(duration, self.timeout)
        self.raise_event(self.STARTED)

    @action
    @raise_event(CANCELED)
    def cancel(self):
        self.timer_native.detach()
        self.raise_event(self.CANCELED)

    @callback(TimerNative.TIMEOUT)
    @raise_event(TIMEOUT)
    def timeout(self):
        self.raise_event(self.TIMEOUT)
