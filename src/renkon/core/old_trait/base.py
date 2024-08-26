from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Sequence

    from polars import DataFrame, Series

    from renkon.core.model import ColumnTypeSet, Schema


type AnyTrait = Trait[*tuple[Any, ...]]
type AnyTraitSketch = TraitSketch[AnyTrait]


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class TraitSketch[T: AnyTrait]:
    """
    Represents a sketch of a trait, where the arity and types of the trait are known,
    but not the parameters.
    """

    trait_type: type[T]
    schema: Schema

    @property
    def arity(self) -> int:
        return len(self.schema)

    def __iter__(self):
        return iter((self.trait_type, self.schema))

    def __str__(self):
        return f"{self.trait_type.__qualname__}({str(self.schema)[1:-1]})"

    def __repr__(self):
        return f"TraitSketch({self.trait_type.__qualname__}, {self.schema})"


@runtime_checkable
class Trait[*ParamTs](Protocol):
    """
    Represents an instantiated sketch. This protocol defines the abstract interface for all traits.
    :cvar meta: the metadata for this trait.
    """

    meta: ClassVar[TraitMeta]

    @property
    @abstractmethod
    def sketch(self) -> TraitSketch[Self]:
        """The sketch that was instantiated into this trait."""
        ...

    @property
    @abstractmethod
    def params(self) -> tuple[*ParamTs]:
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
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self: ...


@runtime_checkable
class TraitMeta(Protocol):
    """
    Represents metadata about a trait used during instantiation and inference.
    """

    @property
    @abstractmethod
    def arity(self) -> int: ...

    @property
    @abstractmethod
    def commutors(self) -> Sequence[bool]: ...

    @property
    @abstractmethod
    def supported_dtypes(self) -> Sequence[ColumnTypeSet]: ...


class BaseTrait[*ParamTs](Trait[*ParamTs], ABC):
    """
    Basic implementation of a trait. This should be appropriate for most traits.
    """

    meta: ClassVar

    _sketch: TraitSketch[Self]
    _params: tuple[*ParamTs]
    _mask: Series
    _score: float

    __slots__ = ("_mask", "_params", "_score", "_sketch")

    def __init__(
        self,
        sketch: TraitSketch[Self],
        params: tuple[*ParamTs],
        mask: Series,
        score: float,
    ):
        self._sketch = sketch
        self._params = params
        self._mask = mask
        self._score = score

    @property
    def sketch(self) -> TraitSketch[Self]:
        return self._sketch

    @property
    def params(self) -> tuple[*ParamTs]:
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
        """
        Infer the sketched trait from the data in a :class:`DataFrame`.

        :param sketch: the sketch to infer, must be of the same type as this trait.
        :param data: the data to infer from.
        """
        ...
