from hw import HWValve
from shelley.shelleypy import operation, system, claim


# @claim("system check G(test -> F ((close & END) | (error & END) | (clean & END)));")
# system check G((test & !(F (clean & END)) & !(F (close & END))) -> F (error & END)); same problem as before
# @claim("system check G(open -> F ((close)));")
# @claim("system check G(test -> ((X (open | clean | test)) & (X (! close))) | END);")
# @claim("system check G((clean & !END) -> X !open);")
# system check G((error & !END) -> X clean); # --> This forces valve to clean everytime there is an error
@system(uses={})
class Counter:
    """
    Water valve that can be tested before run
    Alternatively, a clean procedure might be necessary sometimes before running
    """

    def __init__(self, port):
        self._number_of_people: int = 0

    @operation(initial=True, final=True, next=["inc", "reset"])
    async def inc(self):
        self._number_of_people += 1

    @operation(initial=True, final=True, next=["inc", "reset"])
    async def reset(self):
        self._number_of_people = 0
