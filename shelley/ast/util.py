from __future__ import annotations
from typing import List, TypeVar, Generic

T = TypeVar('T')


class MyCollection(Generic[T]):
    _data: List[T]

    def __init__(self):
        self._data = []

    def add(self, elem: T) -> None:
        if elem not in self._data:
            self._data.append(elem)
        else:
            raise ListDuplicatedError()

    def contains(self, elem: T) -> bool:
        re = False
        try:
            next(x for x in self._data if x == elem)
            re = True
        except StopIteration:
            pass
        return re

    def count(self) -> int:
        return len(self._data)

    def list(self) -> List[T]:
        return self._data

    def list_str(self):
        return [str(elem) for elem in self._data]


class ListDuplicatedError(Exception):
    pass
