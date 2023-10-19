from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from polars import DataFrame, PolarsDataType, Series

if TYPE_CHECKING:
    from renkon.core.strategy import InferenceStrategy


# We're going to be typing this a lot, so an alias is useful.
type TraitType = type[Trait]


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class TraitSketch:
    """
    Represents a sketch of a trait for a given set of columns.
    """

    trait_type: TraitType
    columns: tuple[str, ...]


@runtime_checkable
class Trait(Protocol):
    @classmethod
    @abstractmethod
    def sketch(cls, columns: Sequence[str]) -> TraitSketch:
        """
        :return: a hashable token that uniquely identifies a sketch given some column IDs.
        """
        ...

    @classmethod
    @abstractmethod
    def inference_strategy(cls, priors: tuple[TraitSketch, ...]) -> InferenceStrategy:
        """
        :return: the inference strategy used by this invariant.

        :note: the inference strategy chosen may vary based on provided priors.
        """
        ...

    @classmethod
    @abstractmethod
    def arities(cls) -> tuple[int, ...]:
        """
        :return: the arities supported by this invariant.
        """
        ...

    @classmethod
    @abstractmethod
    def commutors(cls, arity: int) -> tuple[bool, ...]:
        """
        :return: whether this invariant is commutative for each position up to the given arity.

        :note: each position marked True can be swapped with any other position marked True without
               the invariant being considered distinct. For example: Equality.commutors(2) == [True, True]
        """
        ...

    @classmethod
    @abstractmethod
    def dtypes(cls, arity: int) -> tuple[frozenset[PolarsDataType], ...]:
        """
        :return: the types supported for each position up to the given arity.
        """
        ...

    @abstractmethod
    def test(self, data: DataFrame) -> Series:
        """
        :return: boolean Series of whether the trait holds on the given data (for each row).
        """
        ...


class BaseTraitMixin:
    @classmethod
    def sketch(cls: type[Trait], columns: Sequence[str]) -> TraitSketch:
        return TraitSketch(trait_type=cls, columns=tuple(columns))


class PropTrait(BaseTraitMixin, ABC):
    """
    A trait representing a logical proposition, e.g. "x != 0" or "x < y".
    """

    @classmethod
    def satisfy(cls, data: DataFrame) -> Trait | None:
        """
        Attempts to find an assignment of variables (model) that satisfies the proposition on the given data,
        returning a trait instance if successful, or None if no such assignment can be found.
        """
        ...

    def test(self, data: DataFrame) -> Series:
        return self.test_satisfied(data)

    @abstractmethod
    def test_satisfied(self, data: DataFrame) -> Series:
        """
        :return: boolean Series of whether the proposition holds on the given data (for each row).
        """
        ...


class StatTrait(BaseTraitMixin, ABC):
    """
    A trait representing a statistical property, e.g. "x is normally distributed" or "x is linearly correlated with y".
    """

    @classmethod
    @abstractmethod
    def fit[T](cls: type[T], data: DataFrame, columns: list[str]) -> T | None:
        """
        Attempts to fit the statistical property to the given data, returning a trait instance if successful, or
        None if sufficient confidence/goodness-of-fit cannot be achieved.
        """
        ...

    def test(self, data: DataFrame) -> Series:
        return self.test_inlying(data)

    @abstractmethod
    def test_inlying(self, data: DataFrame) -> Series:
        """
        :return: boolean Series of whether the given data is inlying (according to some model).
        """
        ...
