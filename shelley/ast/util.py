from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod
from typing import List, TypeVar, Generic
from shelley.ast.node import Node

if TYPE_CHECKING:
    from shelley.ast.visitors import Visitor

T = TypeVar("T")


class MyCollection(Node, Generic[T]):
    _data: List[T]

    def __init__(self) -> None:
        self._data = []

    def add(self, elem: T) -> None:
        if elem not in self._data:
            self._data.append(elem)
        else:
            raise ListDuplicatedError()

    def contains(self, elem: T) -> bool:
        return elem in self._data

    # TODO: REMOVE THIS
    def count(self) -> int:
        return len(self._data)

    def list(self) -> List[T]:
        return self._data

    def list_str(self) -> List[str]:
        return [str(elem) for elem in self._data]

    def __len__(self):
        return len(self._data)

    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass


class ListDuplicatedError(Exception):
    pass
