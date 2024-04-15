from collections.abc import Sequence
from typing import ClassVar, Self

import polars as pl
from polars import NUMERIC_DTYPES, DataFrame

from renkon.core.schema import ColumnTypeSet
from renkon.core.trait import BaseTrait, TraitMeta, TraitSketch


class Integral(BaseTrait):
    class Meta(TraitMeta):
        @property
        def arity(self) -> int:
            return 1

        @property
        def commutors(self) -> Sequence[bool]:
            return (True,)

        @property
        def supported_dtypes(self) -> Sequence[ColumnTypeSet]:
            return (NUMERIC_DTYPES,)

    meta: ClassVar[Meta] = Meta()

    def __str__(self):
        return f"{self.sketch.schema.columns[0]} ∈ ℤ"  # noqa: RUF001

    @classmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        # Check x % 1 == 0
        col_name = sketch.schema.columns[0]
        mask = data.select(pl.col(col_name).mod(1).eq(0).alias("mask")).to_series()
        score = mask.sum() / len(mask)
        return cls(sketch=sketch, params=(), mask=mask, score=score)
