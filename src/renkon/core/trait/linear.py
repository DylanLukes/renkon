from polars import NUMERIC_DTYPES, DataFrame, DataType, PolarsDataType, Series
from polars.datatypes import DataTypeGroup, NumericType

from renkon.core.stats.linear import OLSModel, OLSResults
from renkon.core.strategy import InferenceStrategy
from renkon.core.trait.base import StatTrait, Trait, TraitSketch, _StatT


class Linear(StatTrait):
    model: OLSModel
    results: OLSResults

    def __init__(self, model: OLSModel, results: OLSResults):
        self.model = model
        self.results = results

    @classmethod
    def inference_strategy(cls, priors: tuple[TraitSketch[Trait], ...]) -> InferenceStrategy:
        raise NotImplementedError

    @classmethod
    def arities(cls) -> tuple[int, ...]:
        return 1, 2, 3, 4

    @classmethod
    def commutors(cls, arity: int) -> tuple[bool, ...]:
        return (False,) + (arity - 1) * (True,)

    @classmethod
    def dtypes(cls, arity: int) -> tuple[frozenset[PolarsDataType], ...]:
        return (NUMERIC_DTYPES,) * arity

    @classmethod
    def fit(cls: type[_StatT], data: DataFrame, columns: list[str]) -> _StatT | None:
        raise NotImplementedError

    def test_inlying(self, data: DataFrame) -> Series:
        raise NotImplementedError
