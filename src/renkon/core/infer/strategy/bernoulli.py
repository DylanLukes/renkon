from __future__ import annotations

from dataclasses import dataclass

from polars import DataFrame, Series

from renkon.core.infer.strategy.base import InferenceStrategy
from renkon.core.trait.base import Trait, TraitSketch


@dataclass(frozen=True, kw_only=True, slots=True)
class BernoulliInferenceStrategy[T: Trait](InferenceStrategy[T]):
    """
    Simple inference strategy which evaluates a simple predicate on the data.
    The confidence rate is determined by a Bernoulli test over the assigned


    By default, this evaluates on _all_ data points.
    TODO: adjust reported confidence for < 100% sample ratio.
    """

    sample_ratio: float = 1.0

    def infer(self, sketch: TraitSketch, data: DataFrame) -> T:
        raise NotImplementedError  # todo: implement

    def test(self, trait: Trait, data: DataFrame) -> Series:
        raise NotImplementedError  # todo: implement

    def score(self, trait: Trait, data: DataFrame) -> float:
        raise NotImplementedError  # todo: implement
