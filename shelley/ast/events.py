from __future__ import annotations
from typing import List, TYPE_CHECKING
from .node import Node

if TYPE_CHECKING:
    from .visitors import Visitor


class GenericEvent(Node):
    name = None  # type: str

    def __init__(self, name: str):
        self.name = name

    #    @abstractmethod -> fix this!
    def accept(self, visitor: Visitor) -> None:
        pass

    def check(self, events: List[GenericEvent]):
        self.check_is_duplicated(events)
        events.append(self)

    def check_is_duplicated(self, events: List[GenericEvent]):
        if self in events:
            raise EventsListDuplicatedError("Duplicated event: {0}".format(self.name))

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
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ievent(self)


class EEvent(GenericEvent):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_eevent(self)


class EventsListEmptyError(Exception):
    pass


class EventsListDuplicatedError(Exception):
    pass
