from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wfsyntax.ast.visitors import Visitor


class Node(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor) -> None:
        pass
