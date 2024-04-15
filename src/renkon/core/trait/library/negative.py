from collections.abc import Sequence
from typing import ClassVar, Self

from polars import NUMERIC_DTYPES, DataFrame

from renkon.core.schema import ColumnTypeSet
from renkon.core.trait import BaseTrait, TraitMeta, TraitSketch


class Negative(BaseTrait[()]):
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
        return f"{self.sketch.schema.columns[0]} ≤ 0"

    @classmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        col = data[sketch.schema.columns[0]]
        mask = col <= 0
        score = mask.sum() / len(mask)
        return cls(sketch=sketch, params=(), mask=mask, score=score)
