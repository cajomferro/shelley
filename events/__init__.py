class GenericEvent:
    name = None

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, GenericEvent):
            # don't attempt to compare against unrelated types
            raise Exception("Instance {0} is not of Event type".format(type(other)))

        return self.name == other.name

    def __str__(self):
        return self.name

    def __hash__(self):
        return id(self.name)


class IEvent(GenericEvent):
    pass


class EEvent(GenericEvent):
    pass
