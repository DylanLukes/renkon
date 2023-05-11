from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from renkon.core.types import Type

_T = TypeVar("_T", bound=Type, covariant=True)


@dataclass(frozen=True, slots=True)
class Hole(Generic[_T]):
    """
    Represents a hole in a Renkon sketch. A hole has a name and an allowed type.
    """

    name: str
    type_: _T

    def __str__(self) -> str:
        return f"{self.name}: {self.type_}"
