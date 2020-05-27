from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
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

    def __init__(self) -> None:
        self._data = []

    def add(self, elem: Event) -> None:
        if elem not in self._data:
            self._data.append(elem)
        else:
            raise EventsListDuplicatedError()

    def contains(self, elem: Event) -> bool:
        return elem in self._data

    def list(self) -> List[Event]:
        return self._data

    def list_str(self) -> List[str]:
        return [str(elem) for elem in self._data]

    def __len__(self):
        return len(self._data)

    def find_by_name(self, name: str) -> Optional[Event]:
        # XXX: This should be the standard method: get
        for x in self._data:
            if x.name == name:
                return x
        return None

    def __getitem__(self, name: str) -> Event:
        res = self.find_by_name(name)
        if res is None:
            raise KeyError(name)
        return res

    def accept(self, visitor: Visitor) -> None:
        visitor.visit_events(self)

    def create(self, name: str, is_start=False, is_final=True) -> Event:
        event = Event(name, is_start, is_final)
        if event not in self._data:
            self._data.append(event)
        else:
            raise EventsListDuplicatedError()
        return event

    def start_events(self) -> List[Event]:
        return [event for event in self._data if event.is_start]

    def final_events(self) -> List[Event]:
        return [event for event in self._data if event.is_final]


class EventsListEmptyError(Exception):
    pass


class EventsListDuplicatedError(Exception):
    pass
