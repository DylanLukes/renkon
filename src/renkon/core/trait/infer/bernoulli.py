from __future__ import annotations

from dataclasses import dataclass

from polars import DataFrame

from renkon.core.trait import Trait, TraitSketch
from renkon.core.trait.infer import InferenceStrategy


@dataclass(frozen=True, kw_only=True, slots=True)
class BernoulliInferenceStrategy[T: Trait](InferenceStrategy[T]):
    """
    Simple inference strategy which evaluates a simple predicate on the data.
    The confidence rate is determined by a Bernoulli test over the assigned


    By default, this evaluates on _all_ data points.
    TODO: adjust reported confidence for < 100% sample ratio.
    """

    sample_ratio: float = 1.0

    def infer(self, sketch: TraitSketch[T], data: DataFrame) -> T:
        raise NotImplementedError

    def score(self, data: DataFrame) -> float:
        raise NotImplementedError
