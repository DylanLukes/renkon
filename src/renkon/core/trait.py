from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar

from polars import DataFrame, Series

if TYPE_CHECKING:
    from renkon.core.inference import InferenceStrategy

_TraitT = TypeVar("_TraitT", bound="Trait")
_PropT = TypeVar("_PropT", bound="PropTrait")
_StatT = TypeVar("_StatT", bound="StatTrait")


class InferenceStrategyKind(Enum):
    """Enumeration for inference strategies."""

    SIMPLE = 0
    """Simple inference strategy. Evaluated by simple predicate."""

    RANSAC = 1
    """RANSAC inference strategy. Valid only for statistical traits."""

    IQR = 2
    """1.5xIQR inference strategy. Valid only for a weaker prior of normality, more robust for smaller datasets."""

    THREE_SIGMA = 3
    """Three-sigma inference strategy. Valid only with a strong prior of normality and sufficient data."""


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class TraitSketch(Generic[_TraitT]):
    trait_type: type[_TraitT]
    column_ids: tuple[str, ...]


class Trait(Protocol):
    @classmethod
    @abstractmethod
    def sketch(cls: type[_TraitT], column_ids: list[str]) -> TraitSketch[_TraitT]:
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

    @property
    @abstractmethod
    def data(self) -> DataFrame:
        """
        :return: the data this trait was inferred from.
        """
        ...

    @abstractmethod
    def test(self, data: DataFrame) -> Series:
        """
        :return: boolean Series of whether the trait holds on the given data (for each row).
        """
        ...


class TypeTrait(Trait, ABC):
    """
    A trait representing a type, e.g. "x is a string" or "x is a number".

    :note: These are in general not inferred but rather provided by the user or taken from the schema.
    """

    # note: should there be a test_coercible?

    pass


class PropTrait(Trait, ABC):
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


class StatTrait(Trait, ABC):
    """
    A trait representing a statistical property, e.g. "x is normally distributed" or "x is linearly correlated with y".
    """

    @classmethod
    def fit(cls: type[_StatT], data: DataFrame) -> _StatT | None:
        """
        Attempts to fit the statistical property to the given data, returning a trait instance if successful, or
        None if sufficient confidence/goodness-of-fit cannot be achieved.
        """
        raise NotImplementedError

    def test(self, data: DataFrame) -> Series:
        return self.test_inlying(data)

    def test_inlying(self, data: DataFrame) -> Series:
        """
        Tests whether each row of the given data is inlying with respect to the statistical property.

        ----

        *Examples:*

        For a normal distribution, this could be whether the data is within 3 standard deviations of the mean.

        For a linear correlation, this could be whether the data is within a 95% confidence interval.

        :return: boolean series of whether the data is inlying with respect to the statistical property (for each row).
        """
        raise NotImplementedError
