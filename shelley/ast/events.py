from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass
from shelley.ast.util import MyCollection
from shelley.ast.node import Node

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


@dataclass(order=True)
class GenericEvent(Node):
    name: str
    is_final: bool
    is_start: bool

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
        # XXX: This should be the standard method: get
        for x in self._data:
            if x.name == name:
                return x
        return None

    def __getitem__(self, name: str) -> GenericEvent:
        res = self.find_by_name(name)
        if res is None:
            raise KeyError(name)
        return res

    def merge(self, events: Events) -> Events:
        merged_events: Events = Events()
        merged_events._data = self._data + events._data
        return merged_events

    # TODO: improve this, do we really need this class?! (this method is not on any visitor and it shouldn't be right?)
    def accept(self, visitor: Visitor) -> None:
        pass


class IEvents(Events):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_ievents(self)

    def create(self, name: str) -> IEvent:
        event = IEvent(name)
        if event not in self._data:
            self._data.append(event)
        else:
            raise EventsListDuplicatedError()
        return event


class EEvents(Events):
    def accept(self, visitor: Visitor) -> None:
        visitor.visit_eevents(self)

    def create(self, name: str, is_start = False, is_final = False) -> EEvent:
        event = EEvent(name, is_start, is_final)
        if event not in self._data:
            self._data.append(event)
        else:
            raise EventsListDuplicatedError()
        return event


class EventsListEmptyError(Exception):
    pass


class EventsListDuplicatedError(Exception):
    pass
