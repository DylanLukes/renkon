from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, runtime_checkable

from polars import DataFrame, DataType, PolarsDataType, Series
from polars.datatypes import DataTypeGroup

if TYPE_CHECKING:
    from renkon.core.strategy import InferenceStrategy

_TraitT = TypeVar("_TraitT", bound="Trait")
_PropT = TypeVar("_PropT", bound="PropTrait")
_StatT = TypeVar("_StatT", bound="StatTrait")


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class TraitSketch(Generic[_TraitT]):
    trait_type: type[_TraitT]
    columns: tuple[str, ...]


@runtime_checkable
class Trait(Protocol):
    @classmethod
    @abstractmethod
    def sketch(cls: type[_TraitT], columns: list[str]) -> TraitSketch[_TraitT]:
        """
        :return: a hashable token that uniquely identifies a sketch given some column IDs.
        """
        ...

    @classmethod
    @abstractmethod
    def inference_strategy(cls, priors: tuple[TraitSketch[Trait], ...]) -> InferenceStrategy:
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


class BaseTrait(Trait, ABC):
    @classmethod
    def sketch(cls: type[_TraitT], columns: list[str]) -> TraitSketch[_TraitT]:
        return TraitSketch(trait_type=cls, columns=tuple(columns))


class PropTrait(BaseTrait, ABC):
    """
    A trait representing a logical proposition, e.g. "x != 0" or "x < y".
    """

    @classmethod
    def satisfy(cls: type[_PropT], data: DataFrame) -> _PropT | None:
        """
        Attempts to find an assignment of variables (model) that satisfies the proposition on the given data,
        returning a trait instance if successful, or None if no such assignment can be found.
        """
        raise NotImplementedError

    def test(self, data: DataFrame) -> Series:
        return self.test_satisfied(data)

    def test_satisfied(self, data: DataFrame) -> Series:
        """
        :return: boolean Series of whether the proposition holds on the given data (for each row).
        """
        raise NotImplementedError


class StatTrait(BaseTrait, ABC):
    """
    A trait representing a statistical property, e.g. "x is normally distributed" or "x is linearly correlated with y".
    """

    @classmethod
    @abstractmethod
    def fit(cls: type[_StatT], data: DataFrame, columns: list[str]) -> _StatT | None:
        """
        Attempts to fit the statistical property to the given data, returning a trait instance if successful, or
        None if sufficient confidence/goodness-of-fit cannot be achieved.
        """
        ...

    @abstractmethod
    def test_inlying(self, data: DataFrame) -> Series:
        """
        Tests whether each row of the given data is inlying with respect to the statistical property.

        ----

        *Examples:*

        For a normal distribution, this could be whether the data is within 3 standard deviations of the mean.

        For a linear correlation, this could be whether the data is within a 95% confidence interval.

        :return: boolean series of whether the data is inlying with respect to the statistical property (for each row).
        """
        ...

    def test(self, data: DataFrame) -> Series:
        return self.test_inlying(data)
