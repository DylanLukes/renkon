from __future__ import annotations

from polars import DataFrame

from renkon.core.trait import Trait, TraitSketch
from renkon.core.trait.infer import InferenceStrategy


class RANSACInferenceStrategy[T: Trait](InferenceStrategy[T]):
    min_sample_size: int
    max_iterations: int
    min_inlier_ratio: float
    min_confidence: float

    def __init__(
        self,
        min_sample_size: int = 2,
        max_iterations: int = 3,
        min_inlier_ratio: float = 0.90,
        min_confidence: float = 0.90,
    ):
        self.min_sample_size = min_sample_size
        self.max_iterations = max_iterations
        self.min_inlier_ratio = min_inlier_ratio
        self.min_confidence = min_confidence

    def infer(self, sketch: TraitSketch[T], data: DataFrame) -> T:
        raise NotImplementedError

    def score(self, data: DataFrame) -> float:
        raise NotImplementedError

    # def infer(self, sketch: TraitSketch, data: DataFrame) -> Linear:
    #     for _i in range(self.max_iterations):
    #         # Take a minimal sample.
    #         # sample_mask =
    #
    #         sample = data.sample(self.min_sample_size)
    #
    #         model = self.base_model_class()
    #         _results = model.fit(sample)
    #         # inliers = model.inliers(data)
    #         # if inliers.size / data.size >= self.min_inlier_ratio:
    #         #     return model
    #
    #     raise NotImplementedError  # todo: implement
    #
    # def score(self, trait: T, data: DataFrame) -> float:
    #     raise NotImplementedError  # todo: implement
