from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from shelley.ast.node import Node
from shelley.ast.util import MyCollection
from dataclasses import dataclass

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


@dataclass(order=True)
class GenericEvent(Node):
    name: str

    def accept(self, visitor: Visitor) -> None:
        pass

    def __str__(self):
        return self.name


class IEvent(GenericEvent):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ievent(self)


class EEvent(GenericEvent):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_eevent(self)


class Events(MyCollection[GenericEvent]):
    def find_by_name(self, name: str) -> Optional[GenericEvent]:
        re: Optional[GenericEvent] = None
        try:
            re = next(x for x in self._data if x.name == name)
        except StopIteration:
            pass
        return re

    def merge(self, events: Events) -> Events:
        merged_events: Events = Events()
        merged_events._data = self._data + events._data
        return merged_events


class IEvents(Node, Events):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ievents(self)

    def create(self, name: str) -> IEvent:
        event = IEvent(name)
        if event not in self._data:
            self._data.append(event)
        else:
            raise EventsListDuplicatedError()
        return event


class EEvents(Node, Events):
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
