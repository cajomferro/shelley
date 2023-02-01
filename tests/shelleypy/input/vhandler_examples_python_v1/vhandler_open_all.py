from shelley.shelleypy import operation, system, claim
from machine import Pin


@system(uses={})
class VHandlerOpenAll:

    @operation(initial=True, next=["b_open"])
    def a_open(self):
        return "b_open"

    @operation(final=True, next=[])
    def b_open(self):
        return "a_open"