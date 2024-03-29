from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar, Protocol, Self, runtime_checkable

from polars import DataFrame, Series

from renkon.core.schema import ColumnTypeSet, Schema


def infer[T: "Trait"](_sketch: TraitSketch[T], _data: DataFrame) -> T:
    raise NotImplementedError


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class TraitSketch[T: "Trait"]:
    """
    Represents a sketch of a trait, where the arity and types of the trait are known,
    but not the parameters.
    """

    trait_type: type[Trait]
    schema: Schema

    @property
    def arity(self) -> int:
        return len(self.schema)

    def __lt__(self, other):
        return (self.trait_type.__name__, self.schema) < (other.trait_type.__name__, other.schema)

    def __iter__(self):
        return iter((self.trait_type, self.schema))

    def __str__(self):
        return f"{self.trait_type.__qualname__}({str(self.schema)[1:-1]})"

    def __repr__(self):
        return f"TraitSketch({self.trait_type.__qualname__}, {self.schema})"


@runtime_checkable
class TraitMeta[T: "Trait"](Protocol):
    """
    Represents metadata about a trait used during instantiation and inference.
    """

    @property
    @abstractmethod
    def arity(self) -> int:
        ...

    @property
    @abstractmethod
    def commutors(self) -> Sequence[bool]:
        ...

    @property
    @abstractmethod
    def supported_dtypes(self) -> Sequence[ColumnTypeSet]:
        ...


@runtime_checkable
class Trait(Protocol):
    """
    Represents an instantiated sketch. This protocol defines the abstract interface for all traits.
    :cvar meta: the metadata for this trait.
    """

    meta: ClassVar[TraitMeta[Self]]

    @property
    @abstractmethod
    def sketch[T: "Trait"](self: T) -> TraitSketch[T]:
        """The sketch that was instantiated into this trait."""
        ...

    @property
    @abstractmethod
    def params(self) -> tuple[object, ...] | None:
        """The inferred parameters of the trait."""
        ...

    @property
    @abstractmethod
    def mask(self) -> Series:
        """A boolean Series of whether each row matches (inlies/satisfies) the trait."""
        ...

    @property
    @abstractmethod
    def score(self) -> float:
        """A [0,1] confidence of the trait."""
        ...

    @classmethod
    @abstractmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        ...


class BaseTrait[T: "BaseTrait"](Trait, ABC):
    """
    Basic implementation of a trait. This should be appropriate for most traits.
    """

    meta: ClassVar

    _sketch: TraitSketch[T]
    _params: tuple[object, ...]
    _mask: Series
    _score: float

    def __init__(self, sketch: TraitSketch[T], params: tuple[object, ...], mask: Series, score: float):
        self._sketch = sketch
        self._params = params
        self._mask = mask
        self._score = score

    @property
    def sketch(self) -> TraitSketch[T]:
        return self._sketch

    @property
    def params(self) -> tuple[object, ...] | None:
        return self._params

    @property
    def mask(self) -> Series:
        return self._mask

    @property
    def score(self) -> float:
        return self._score

    @classmethod
    @abstractmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        ...
