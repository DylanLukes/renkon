from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, runtime_checkable

from polars import DataFrame, Series

from renkon.core.schema import ColumnTypeSet, Schema

if TYPE_CHECKING:
    from renkon.core.infer.strategy import InferenceStrategy


# We're going to be typing this a lot, so an alias is useful.
# type TraitType = type[Trait]


def infer(_sketch: TraitSketch, _data: DataFrame) -> Trait:
    raise NotImplementedError


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class TraitSketch:
    """
    Represents a sketch of a trait, where the arity and types of the trait are known,
    but not the parameters.
    """

    trait_type: type[Trait]
    schema: Schema

    @property
    def arity(self) -> int:
        return len(self.schema)

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
    def dtypes(self) -> Sequence[ColumnTypeSet]:
        ...

    @property
    @abstractmethod
    def inference_strategy(self) -> InferenceStrategy[T]:
        ...


class Trait(Protocol):
    """
    Represents an instantiated sketch. This protocol defines the abstract interface for all traits.
    :cvar meta: the metadata for this trait.
    """

    meta: ClassVar[TraitMeta[Self]]

    @property
    @abstractmethod
    def sketch(self) -> TraitSketch:
        """The sketch that instantiated this trait."""
        ...

    @property
    @abstractmethod
    def params(self) -> tuple[object, ...]:
        """The inferred parameters of the trait."""
        ...

    @property
    @abstractmethod
    def score(self) -> float:
        """A [0,1] confidence of the trait."""
        ...

    @property
    @abstractmethod
    def matches(self) -> Series:
        """A boolean Series of whether each row matches (inlies/satisfies) the trait."""
        ...


class BaseTrait(Trait, Protocol):
    """
    Basic implementation of a trait. This should be appropriate for most traits.
    """

    _sketch: TraitSketch
    _params: tuple[Any]
    _score: float
    _matches: Series

    def __init__(self, sketch: TraitSketch, params: tuple[Any], score: float, matches: Series):
        self._sketch = sketch
        self._params = params
        self._score = score
        self._matches = matches

    @property
    def sketch(self) -> TraitSketch:
        return self._sketch

    @property
    def params(self) -> tuple[Any]:
        return self._params

    @property
    def score(self) -> float:
        return self._score

    @property
    def matches(self) -> Series:
        return self._matches
