from native.generic.timer import Timer
from unittest.mock import MagicMock

# https://docs.python.org/3/library/typing.html#callable
from typing import Callable

Ticker = MagicMock()


class ArduinoTimer(Timer):
    ticker = None

    def __init__(self):
        super()
        self.ticker = Ticker()

    def attach(self, seconds: float, callback: Callable[[], None]):
        self.ticker.attach(seconds, lambda: self._isr(Timer.TIMEOUT))
        self.subscribe(Timer.TIMEOUT, callback)

    def detach(self):
        self.ticker.detach()

    def isr(self, event):
        self.raise_event(event)
