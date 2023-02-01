from shelley.shelleypy import operation, system, claim
from machine import Pin


@system(uses={})
class VHandlerOpenAll:

    @operation(initial=True, next=["b_close"])
    def a_close(self):
        return "b_close"

    @operation(final=True, next=[])
    def b_close(self):
        return "a_close"