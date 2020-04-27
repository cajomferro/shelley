from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, Optional
from .node import Node
from .util import MyCollection
from dataclasses import dataclass

if TYPE_CHECKING:
    from .visitors import Visitor


@dataclass(order=True)
class GenericEvent(Node):
    name: str

    # def __new__(cls, name: str):
    #     instance = find_instance_by_name(name, events)
    #     if instance is None:
    #         instance = super(GenericEvent, cls).__new__(cls)
    #         events.append(instance)
    #     return instance

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ievent(self)

    # def check(self, events: Set[GenericEvent]):
    #     self.check_is_duplicated(events)
    #     events.add(self)
    #
    # def check_is_duplicated(self, events: Set[GenericEvent]):
    #     if self in events:
    #         raise EventsListDuplicatedError("Duplicated event: {0}".format(self.name))

    def __str__(self):
        return self.name

    # def __eq__(self, other):
    #     if not isinstance(other, GenericEvent):
    #         # don't attempt to compare against unrelated types
    #         raise Exception("Instance {0} is not of Event type".format(type(other)))
    #
    #     return self.name == other.name
    #
    # def __hash__(self):
    #     return id(self.uuid


class IEvent(GenericEvent):

    # def __new__(cls, name: str):
    #     instance = find_instance_by_name(name, events)
    #     if instance is None:
    #         instance = super(IEvent, cls).__new__(cls, name)
    #         events.append(instance)
    #     return instance

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ievent(self)


class EEvent(GenericEvent):

    # def __new__(cls, name: str):
    #     instance = find_instance_by_name(name, events)
    #     if instance is None:
    #         instance = super(EEvent, cls).__new__(cls, name)
    #         events.append(instance)
    #     return instance

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_eevent(self)


X = TypeVar('X', IEvent, EEvent, GenericEvent)


class Events(MyCollection[X]):

    def find_by_name(self, name: str) -> Optional[GenericEvent]:
        re: Optional[GenericEvent] = None
        try:
            re = next(x for x in self._data if x.name == name)
        except StopIteration:
            pass
        return re

    def merge(self, events: Events[X]) -> Events[X]:
        merged_events: Events[X] = Events()
        merged_events._data = self._data + events._data
        return merged_events


class IEvents(Node, Events[IEvent]):

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ievents(self)

    def create(self, name: str) -> IEvent:
        event = IEvent(name)
        if event not in self._data:
            self._data.append(event)
        else:
            raise EventsListDuplicatedError()
        return event


class EEvents(Node, Events[EEvent]):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_eevents(self)

    def create(self, name: str) -> EEvent:
        event = EEvent(name)
        if event not in self._data:
            self._data.append(event)
        else:
            raise EventsListDuplicatedError()
        return event


class EventsListEmptyError(Exception):
    pass


class EventsListDuplicatedError(Exception):
    pass
