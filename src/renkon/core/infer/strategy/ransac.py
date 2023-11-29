from __future__ import annotations

from dataclasses import dataclass

from polars import DataFrame

from renkon.core.infer.strategy import InferenceStrategy
from renkon.core.trait import Linear
from renkon.core.trait.base import TraitSketch


@dataclass(eq=True, frozen=True, kw_only=True, slots=True)
class RANSACInferenceStrategy(InferenceStrategy[Linear]):
    min_sample: int = 2
    max_iterations: int = 3
    min_inlier_ratio: float = 0.90
    min_confidence: float = 0.90

    def infer(self, sketch: TraitSketch, data: DataFrame) -> Linear:
        for _i in range(self.max_iterations):
            # Take a minimal sample.
            # sample_mask =

            sample = data.sample(self.min_sample)

            model = self.base_model_class()
            _results = model.fit(sample)
            # inliers = model.inliers(data)
            # if inliers.size / data.size >= self.min_inlier_ratio:
            #     return model

        raise NotImplementedError  # todo: implement

    def score(self, trait: T, data: DataFrame) -> float:
        raise NotImplementedError  # todo: implement
