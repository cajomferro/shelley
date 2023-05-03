from shelley.shelleypy import operation, system, claim


@system(uses={})
class EventHandler:
    def __init__(self):
        self._events = []  # TODO: this should be somehow an internal list to pyControl where events will be added

    @op_initial
    def next(self):
        if not len(self._events):
            return "nop"

        event = self._events.pop()
        # if event == "entry":
        #     return "entry"
        # elif event == "exit":
        #     return "exit"
        if event == "center_poke":
            return "center_poke"
        elif event == "left_poke":
            return "left_poke"
        elif event == "right_poke":
            return "right_poke"
        elif event == "session_timer":
            return "session_timer"
        else:
            return "error"

    # @operation(final=True, next=["next"])
    # def entry(self):
    #     return "next"
    #
    # @operation(final=True, next=["next"])
    # def exit(self):
    #     return "next"

    @op_final
    def center_poke(self):
        print("center_poke event")
        return "next"

    @op_final
    def left_poke(self):
        print("left_poke event")
        return "next"

    @op_final
    def right_poke(self):
        print("right_poke event")
        return "next"

    @op_final
    def session_timer(self):
        print("session_timer event")
        return "next"

    @op_final
    def error(self):
        print("error event")
        return "next"

    @op_final
    def nop(self):
        print("nop event")
        return "next"