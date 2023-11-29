from __future__ import annotations

from polars import NUMERIC_DTYPES, DataFrame, PolarsDataType, Series

from renkon.core.infer.strategy import InferenceStrategy, RANSACInferenceStrategy
from renkon.core.stats.linear import OLSModel
from renkon.core.trait.base import Trait


class Linear(Trait):
    @classmethod
    def inference_strategy(cls) -> InferenceStrategy:
        return RANSACInferenceStrategy(min_sample=2, base_model=OLSModel)

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

    def test(self, data: DataFrame) -> Series:
        raise NotImplementedError
