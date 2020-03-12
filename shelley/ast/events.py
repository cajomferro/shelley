from __future__ import annotations
from typing import Set, TYPE_CHECKING
import uuid
from .node import Node

if TYPE_CHECKING:
    from .visitors import Visitor


class GenericEvent(Node):
    uuid = uuid.uuid1()
    name = None  # type: str

    def __init__(self, name: str):
        self.name = name

    #    @abstractmethod -> fix this!
    def accept(self, visitor: Visitor) -> None:
        pass

    # def check(self, events: Set[GenericEvent]):
    #     self.check_is_duplicated(events)
    #     events.add(self)
    #
    # def check_is_duplicated(self, events: Set[GenericEvent]):
    #     if self in events:
    #         raise EventsListDuplicatedError("Duplicated event: {0}".format(self.name))

    def __eq__(self, other):
        if not isinstance(other, GenericEvent):
            # don't attempt to compare against unrelated types
            raise Exception("Instance {0} is not of Event type".format(type(other)))

        return self.name == other.name

    def __str__(self):
        return self.name

    def __hash__(self):
        return id(self.uuid)


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
