from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from typing import Any, Self

from polars import NUMERIC_DTYPES, DataFrame, Utf8

from renkon.core.schema import ColumnTypeSet
from renkon.core.trait import BaseTrait, TraitMeta, TraitSketch


class Equal(BaseTrait[Self], ABC):
    class Meta(TraitMeta[Self]):
        _types: ColumnTypeSet

        def __init__(self, types: ColumnTypeSet):
            self._types = types

        @property
        def arity(self) -> int:
            return 2

        @property
        def commutors(self) -> Sequence[bool]:
            return True, True

        @property
        def supported_dtypes(self) -> Sequence[ColumnTypeSet]:
            return self._types, self._types

    def __init_subclass__(cls, *, types: ColumnTypeSet, **kwargs: Any):
        cls.meta = Equal.Meta(types=types)
        super().__init_subclass__(**kwargs)

    def __str__(self):
        return f"{self.sketch.schema.columns[0]} == {self.sketch.schema.columns[1]}"

    @classmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        lhs, rhs = sketch.schema.columns
        mask = data[lhs] == data[rhs]
        score = mask.sum() / len(mask)

        return cls(sketch=sketch, params=(), mask=mask, score=score)


class EqualNumeric(Equal, types=NUMERIC_DTYPES):
    pass


class EqualString(Equal, types=frozenset([Utf8])):
    pass
