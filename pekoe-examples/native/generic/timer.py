from decorators import *
from native.generic import Native
# https://docs.python.org/3/library/typing.html#callable
from typing import Callable


class Timer(Native):
    TIMEOUT = 0

    def __init__(self):
        super()

    @interface
    def attach(self, seconds: float, callback: Callable[[], None]):
        pass

    @interface
    def detach(self):
        pass

    @interface
    def isr(self, event):
        pass
