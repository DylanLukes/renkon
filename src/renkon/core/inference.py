from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from polars import DataFrame, Series

from renkon.core.trait import Trait, TraitSketch, _TraitT


class InferenceStrategy(Protocol):
    def infer(self, sketch: TraitSketch[_TraitT], data: DataFrame) -> _TraitT:
        """
        :return: an invariant inferred from the given data.
        """
        raise NotImplementedError

    def test(self, trait: Trait, data: DataFrame) -> Series:
        """
        :param trait: the trait to evaluate.
        :param data: the data to evaluate on (may include the training data, but also test data)
        :return: a boolean series indicating the rows where the trait holds.
        """
        raise NotImplementedError

    def confidence(self, trait: Trait, data: DataFrame) -> float:
        """
        :param trait: the trait to evaluate.
        :param data: the data to evaluate on (may include the training data, but also test data)
        :return: evaluate the confidence of the inferred trait on the given data.
        """
        raise NotImplementedError


@dataclass(frozen=True, kw_only=True, slots=True)
class RANSACInferenceStrategy(InferenceStrategy):
    min_sample: int
    max_iterations: int = 3
    min_inlier_ratio: float = 0.90
    min_confidence: float = 0.90

    def infer(self, sketch: TraitSketch[_TraitT], data: DataFrame) -> _TraitT:
        raise NotImplementedError  # todo: implement

    def test(self, trait: Trait, data: DataFrame) -> Series:
        raise NotImplementedError  # todo: implement

    def confidence(self, trait: Trait, data: DataFrame) -> float:
        raise NotImplementedError  # todo: implement


@dataclass(frozen=True, kw_only=True, slots=True)
class SimpleInferenceStrategy(InferenceStrategy):
    """
    Simple inference strategy which evaluates a simple predicate on the data.

    By default, this evaluates on _all_ data points.
    TODO: adjust reported confidence for < 100% sample ratio.
    """

    sample_ratio: float = 1.0

    def infer(self, sketch: TraitSketch[_TraitT], data: DataFrame) -> _TraitT:
        raise NotImplementedError  # todo: implement

    def test(self, trait: Trait, data: DataFrame) -> Series:
        raise NotImplementedError  # todo: implement

    def confidence(self, trait: Trait, data: DataFrame) -> float:
        raise NotImplementedError  # todo: implement


@dataclass(frozen=True, kw_only=True, slots=True)
class ThreeSigmaInferenceStrategy(InferenceStrategy):
    def infer(self, sketch: TraitSketch[_TraitT], data: DataFrame) -> _TraitT:
        raise NotImplementedError  # todo: implement

    def test(self, trait: Trait, data: DataFrame) -> Series:
        raise NotImplementedError

    def confidence(self, trait: Trait, data: DataFrame) -> float:
        raise NotImplementedError
