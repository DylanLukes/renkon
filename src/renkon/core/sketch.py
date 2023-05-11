from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from renkon.core import types
from renkon.core.hole import Hole
from renkon.core.types import Float
from renkon.core.types.type import AnyType, Int

_T = TypeVar("_T", bound=AnyType, covariant=True)
_NumT = TypeVar("_NumT", bound=Int | Float, covariant=True)


class Sketch(Protocol):
    """
    Represents a sketch of a property, potentially with holes.

    Note that a sketch is an instance of a Sketch class, not the class itself.
    For example, Linear(2) and Linear(3) are both distinct sketches.
    """

    __slots__ = ("arity", "holes")

    arity: int
    """The number of variables in the sketch."""

    holes: tuple[Hole[AnyType], ...]
    """The holes in the sketch."""

    def __str__(self) -> str:
        ...


class Linear(Sketch):
    """
    Sketch of a linear relationship between two or more variables
    of the form y = a_0*x_0 + a_1*x_1 + ... + a_n*x_n + b.

    Arity: n + 1
    Holes: a_0, a_1, ..., a_n, b
    """

    arity: int
    holes: tuple[Hole[Float], ...]

    def __init__(self, arity: int) -> None:
        self.arity = arity
        holes = [Hole(f"a_{i}", types.float64) for i in range(arity)]
        holes.append(Hole("b", types.float64))
        self.holes = tuple(holes)


class Equal(Sketch, Generic[_T]):
    arity = 2
    holes: tuple[()] = ()

    def __str__(self) -> str:
        return "_0 == _1"


class FuzzyEqual(Sketch, Generic[_NumT]):
    arity = 2
    holes: tuple[Hole[_NumT]]

    def __init__(self, type_: _NumT) -> None:
        self.holes = (Hole("tol", type_),)

    def __str__(self) -> str:
        return f"_0 == _1 +- {self.holes[0].name}"


class BoundedAbove(Sketch, Generic[_NumT]):
    arity: int = 1
    holes: tuple[Hole[_NumT]]

    def __init__(self, type_: _NumT) -> None:
        self.holes = (Hole("u", type_),)

    def __str__(self) -> str:
        return f"_0 ≤ {self.holes[0].name}"


class BoundedBelow(Sketch, Generic[_NumT]):
    arity: int = 1
    holes: tuple[Hole[_NumT]]

    def __init__(self, type_: _NumT) -> None:
        self.holes = (Hole("l", type_),)

    def __str__(self) -> str:
        return f"_0 ≥ {self.holes[0].name}"
