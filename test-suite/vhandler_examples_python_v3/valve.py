from hw import HWValve
from shelley.shelleypy import operation, system, claim


# @claim("system check G(test -> F ((close & END) | (error & END) | (clean & END)));")
# system check G((test & !(F (clean & END)) & !(F (close & END))) -> F (error & END)); same problem as before
@claim("system check G(open -> F ((close)));")
@claim("system check G(test -> ((X (open | clean | test)) & (X (! close))) | END);")
@claim("system check G((clean & !END) -> X !open);")
# system check G((error & !END) -> X clean); # --> This forces valve to clean everytime there is an error
@system(uses={})
class Valve:
    """
    Water valve that can be tested before run
    Alternatively, a clean procedure might be necessary sometimes before running
    """

    def __init__(self, port):
        self._valve = HWValve(port)

    @operation(initial=True, final=True, next=["open", "clean", "test"])
    def test(self):
        if self._valve.is_working():
            return "open"
        else:
            return ["clean", "test"] # THIS SHOULD NOT BE POSSIBLE BECAUSE WHOEVER USES THIS CAN HAVE AN INFINITE LOOP (see twovalves.py for example)

    @operation(next=["close"])
    def open(self):
        self._valve.open()

    @operation(final=True, next=["test"])
    def clean(self):
        self._valve.clean()

    @operation(final=True, next=["test"])
    def close(self):
        self._valve.close()
