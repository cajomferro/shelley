from decorators import *
from native.generic import Native


class DigitalOutput(Native):

    def __init__(self):
        super()

    @interface
    def high(self):
        pass

    @interface
    def low(self):
        pass
