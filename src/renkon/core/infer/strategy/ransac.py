from __future__ import annotations

from dataclasses import dataclass
from typing import override

from polars import DataFrame, Series

from renkon.core.infer.strategy.base import InferenceStrategy
from renkon.core.stats.base import Model, ModelParams
from renkon.core.trait.base import Trait, TraitSketch


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class RANSACInferenceStrategy[P: ModelParams](InferenceStrategy):
    base_model: Model[P]
    min_sample: int
    max_iterations: int = 3
    min_inlier_ratio: float = 0.90
    min_confidence: float = 0.90

    @override
    def infer(self, sketch: TraitSketch, data: DataFrame) -> Trait:
        for i in range(self.max_iterations):
            # Take a minimal sample.
            sample = data.sample(self.min_sample)

            # sample = sketch.sample(self.min_sample)
            # model = self.base_model.fit(data, sample)
            # inliers = model.inliers(data)
            # if inliers.size / data.size >= self.min_inlier_ratio:
            #     return model

        raise NotImplementedError  # todo: implement

    @override
    def test(self, trait: Trait, data: DataFrame) -> Series:
        raise NotImplementedError  # todo: implement

    @override
    def score(self, trait: Trait, data: DataFrame) -> float:
        raise NotImplementedError  # todo: implement
