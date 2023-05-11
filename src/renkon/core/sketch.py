from __future__ import annotations

from abc import ABC
from typing import Literal

from renkon.core import types
from renkon.core.hole import Hole
from renkon.core.types import Float, Type


class Sketch(ABC):
    """
    Represents a sketch of a property, potentially with holes.

    Note that a sketch is an instance of a Sketch class, not the class itself.
    For example, Linear(2) and Linear(3) are both distinct sketches.
    """

    __slots__ = ("arity", "holes")

    arity: int
    holes: tuple[Hole[Type], ...]


class Linear(Sketch):
    """
    Sketch of a linear relationship between two or more variables
    of the form y = a_0*x_0 + a_1*x_1 + ... + a_n*x_n + a_{n+1}.

    Arity: n + 1
    Holes: a_0, a_1, ..., a_n
    """

    arity: int
    holes: tuple[Hole[Float], ...]

    def __init__(self, n_vars: int) -> None:
        self.arity = n_vars + 1
        self.holes = tuple(Hole(f"a_{i}", types.float64) for i in range(n_vars + 1))
