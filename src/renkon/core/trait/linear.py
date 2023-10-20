from __future__ import annotations

from polars import NUMERIC_DTYPES, DataFrame, PolarsDataType, Series

from renkon.core.stats.linear import OLSModel, OLSModelResults
from renkon.core.strategy import InferenceStrategy, RANSACInferenceStrategy
from renkon.core.trait.base import StatTrait, TraitSketch


class Linear(StatTrait):
    model: OLSModel
    results: OLSModelResults

    def __init__(self, model: OLSModel, results: OLSModelResults):
        self.model = model
        self.results = results

    @classmethod
    def inference_strategy(cls, _priors: tuple[TraitSketch, ...]) -> InferenceStrategy:
        return RANSACInferenceStrategy(min_sample=2)

    @classmethod
    def arities(cls) -> tuple[int, ...]:
        return 2, 3, 4

    @classmethod
    def commutors(cls, arity: int) -> tuple[bool, ...]:
        return (False,) + (arity - 1) * (True,)

    @classmethod
    def dtypes(cls, arity: int) -> tuple[frozenset[PolarsDataType], ...]:
        return (NUMERIC_DTYPES,) * arity

    @classmethod
    def fit(cls, data: DataFrame, columns: list[str]) -> Linear | None:
        raise NotImplementedError

    def test_inlying(self, data: DataFrame) -> Series:
        raise NotImplementedError
