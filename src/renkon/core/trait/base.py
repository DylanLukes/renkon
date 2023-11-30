from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Protocol, Self, runtime_checkable

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
    _params: tuple[Any]
    _score: float
    _matches: Series

    def __init__(self, sketch: TraitSketch[T], params: tuple[Any], score: float, matches: Series):
        self._sketch = sketch
        self._params = params
        self._score = score
        self._matches = matches

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        # If meta is defined, continue.
        if hasattr(cls, "meta"):
            return

        # Otherwise, check for a Meta class and try to instantiate it.
        if hasattr(cls, "Meta"):
            try:
                cls.meta = cls.Meta()  # type: ignore
                return
            except Exception as e:
                msg = f"{cls.__name__}'s Meta class could not be instantiated."
                raise RuntimeError(msg) from e

        # Otherwise, we have no meta, so raise an error.
        msg = f"{cls.__name__} has no meta class-var or Meta inner-class defined."
        raise RuntimeError(msg)

    @property
    def sketch(self) -> TraitSketch[T]:
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

    @classmethod
    @abstractmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        ...
