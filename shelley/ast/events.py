from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List, Dict
from dataclasses import dataclass
from shelley.ast.node import Node

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor


@dataclass(order=True)
class Event(Node):
    name: str
    is_start: bool
    is_final: bool

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_event(self)

    def __str__(self):
        return self.name


class Events(Node):
    _data: List[Event]
    _events: Dict[str, Event]

    def __init__(self) -> None:
        self._data = []
        self._events = dict()

    def add(self, elem: Event) -> None:
        if elem.name in self._events:
            raise EventsListDuplicatedError()

        self._events[elem.name] = elem
        self._data.append(elem)

    def contains(self, elem: Event) -> bool:
        return elem in self._data

    def list(self) -> List[Event]:
        return self._data

    def list_str(self) -> List[str]:
        return [str(elem) for elem in self._data]

    def __len__(self):
        return len(self._data)

    def find_by_name(self, name: str) -> Optional[Event]:
        return self._events.get(name, None)

    def __getitem__(self, name: str) -> Event:
        return self._events[name]

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_events(self)

    def create(self, name: str, is_start=False, is_final=True) -> Event:
        event = Event(name, is_start, is_final)
        self.add(event)
        return event

    def start_events(self) -> List[Event]:
        return [event for event in self._data if event.is_start]

    def final_events(self) -> List[Event]:
        return [event for event in self._data if event.is_final]


class EventsListEmptyError(Exception):
    pass


class EventsListDuplicatedError(Exception):
    pass
