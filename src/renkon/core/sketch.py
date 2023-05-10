from __future__ import annotations

from abc import ABC
from typing import Any, Literal, TypeVar

from renkon.core import rkty
from renkon.core.hole import Filled, Hole
from renkon.core.rkty import (
    RkAnyTy,
    RkFloatTy,
    RkNumberTy,
)

_RkTy = TypeVar("_RkTy", bound=RkAnyTy, covariant=True)
_RkNumTy = TypeVar("_RkNumTy", bound=RkNumberTy, covariant=True)


class Sketch(ABC):
    """
    Represents a sketch of a property, potentially with holes.

    Note that a sketch is an instance of a Sketch class, not the class itself.
    For example, Linear(2) and Linear(3) are both distinct sketches.
    """

    __slots__ = ("arity", "holes")

    arity: int
    holes: tuple[Hole[Any, Literal[Filled.NO]], ...]


class Linear(Sketch):
    """
    Sketch of a linear relationship between two or more variables
    of the form y = a_0*x_0 + a_1*x_1 + ... + a_n*x_n + a_{n+1}.

    Arity: n + 1
    Holes: a_0, a_1, ..., a_n
    """

    arity: int
    holes: tuple[Hole[RkFloatTy, Literal[Filled.NO]], ...]

    def __init__(self, n_vars: int) -> None:
        self.arity = n_vars + 1
        self.holes = tuple(Hole.empty(f"a_{i}", rkty.float64()) for i in range(n_vars + 1))
