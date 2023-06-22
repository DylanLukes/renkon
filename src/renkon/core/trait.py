from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Generic, Protocol, TypeVar

_TraitT = TypeVar("_TraitT", bound="Trait")


class TraitState(Enum):
    """ """

    SKETCHED = 0
    INFERRED = 1


class InferenceStrategy(Enum):
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
    def sketch(cls) -> TraitSketch[_TraitT]:
        """
        :return: a hashable token that uniquely identifies a sketch given some column IDs.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def inference_strategy(cls, priors: tuple[TraitSketch, ...]) -> InferenceStrategy:
        """
        :return: the inference strategy used by this invariant.

        :note: the inference strategy chosen may vary based on provided priors.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def arities(cls) -> tuple[int, ...]:
        """
        :return: the arities supported by this invariant.
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def commutors(cls, arity: int) -> tuple[bool, ...]:
        """
        :return: whether this invariant is commutative for each position up to the given arity.

        :note: each position marked True can be swapped with any other position marked True without
               the invariant being considered distinct. For example:


        """
        raise NotImplementedError


class PropTrait(Trait, Protocol):
    """
    A trait representing a logical proposition, e.g. "x > 0" or "x < y".
    """

    pass


class StatTrait(Trait, Protocol):
    """
    A trait representing a statistical property, e.g. "x is normally distributed" or "x is linearly correlated with y".
    """

    pass
