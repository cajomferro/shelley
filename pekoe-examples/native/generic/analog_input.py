from decorators import *
from native.generic import Native


class AnalogInput(Native):
    FALL = 0
    RISE = 1

    def __init__(self):
        super()

    @interface
    def attach_rise(self, callback):
        pass

    @interface
    def attach_fall(self, callback):
        pass

    @interface
    def isr(self, event):
        pass
