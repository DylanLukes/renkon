from __future__ import annotations

from abc import ABC
from collections.abc import Callable, Sequence
from typing import Any, ClassVar, Self

import numpy as np
import polars as pl
from loguru import logger
from polars import FLOAT_DTYPES, NUMERIC_DTYPES, DataFrame, Utf8

from renkon.core.model import ColumnTypeSet, Schema
from renkon.core.old_trait import BaseTrait, TraitMeta, TraitSketch

type SeriesComparator = Callable[[pl.Series, pl.Series, Schema], pl.Series]


class Compare(BaseTrait[()], ABC):
    compare: ClassVar[SeriesComparator]

    class Meta(TraitMeta):
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

    def __init_subclass__(cls, *, types: ColumnTypeSet, compare: SeriesComparator, **kwargs: Any):
        cls.meta = Compare.Meta(types=types)
        cls.compare = compare
        super().__init_subclass__(**kwargs)

    def __str__(self):
        return f"{self.sketch.schema.columns[0]} == {self.sketch.schema.columns[1]}"

    @classmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        lhs, rhs = sketch.schema.columns
        mask = cls.compare(data[lhs], data[rhs], sketch.schema)
        score = mask.sum() / len(mask)
        return cls(sketch=sketch, params=(), mask=pl.Series(mask), score=score)


def default_eq(lhs: pl.Series, rhs: pl.Series, _schema: Schema) -> pl.Series:
    """Default equality comparator which uses the equality operator."""
    return lhs == rhs


def numeric_eq(lhs: pl.Series, rhs: pl.Series, schema: Schema) -> pl.Series:
    """
    Equality comparator for numeric types which uses the equality operator,
    but in the case of floats uses np.isclose.
    """
    if set(schema.dtypes) & FLOAT_DTYPES:
        logger.warning(f"Sketch {schema} contains floats, using fuzzy check with rtol=1.e-5, atol=1.e-8.")
        return pl.Series(np.isclose(lhs, rhs))

    return default_eq(lhs, rhs, schema)


class EqualNumeric(Compare, types=NUMERIC_DTYPES, compare=numeric_eq):
    pass


class EqualString(Compare, types=frozenset([Utf8]), compare=default_eq):
    pass


class EqualTemporal(
    Compare,
    types=frozenset([pl.Date, pl.Datetime, pl.Time, pl.Duration]),
    compare=default_eq,
):
    pass
