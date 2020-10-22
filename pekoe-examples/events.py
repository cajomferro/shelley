import time
from typing import Callable  # https://docs.python.org/3/library/typing.html#callable
from devices import Device


class Event:
    callback = None  # type: Callable[[int], None]
    timestamp = None  # type: float

    def __init__(self, callback: Callable[[int], None]):
        self.callback = callback
        self.timestamp = time.time()


class NativeEvent:
    callback = None  # type: Callable[[int], None]
    timestamp = None  # type: float

    def __init__(self, callback: Callable[[int], None]):
        self.callback = callback
        self.timestamp = time.time()
