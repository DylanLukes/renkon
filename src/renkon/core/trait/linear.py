from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from typing import Any, Self

import numpy as np
import polars as pl
import rich
from polars import NUMERIC_DTYPES, DataFrame
from sklearn.linear_model import LinearRegression, RANSACRegressor

from renkon.core.schema import ColumnTypeSet
from renkon.core.trait import TraitSketch
from renkon.core.trait.base import BaseTrait, TraitMeta


class Linear(BaseTrait[Self], ABC):
    class Meta(TraitMeta[Self]):
        _arity: int

        def __init__(self, arity: int):
            self._arity = arity

        @property
        def arity(self) -> int:
            return self._arity

        @property
        def commutors(self) -> Sequence[bool]:
            return (False,) * self.arity
            # return (False,) + (self.arity - 1) * (True,)
            # return (True,) * self.arity

        @property
        def supported_dtypes(self) -> Sequence[ColumnTypeSet]:
            return (NUMERIC_DTYPES,) * self.arity

    def __init_subclass__(cls, *, arity: int, **kwargs: Any):  # type: ignore
        cls.meta = Linear.Meta(arity=arity)
        super().__init_subclass__(**kwargs)

    def __str__(self):
        # Format in y = mx + b form with coefs.
        y_col, *x_cols = self.sketch.schema.columns
        cs = self.params[:-1]
        m = self.params[-1]

        coef_str = " + ".join(f"({c:.2f} × {x})" for c, x in zip(cs, x_cols, strict=True))

        return f"{y_col} = {coef_str} + {m:.2f}"

    @classmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        y_col, *x_cols = sketch.schema.columns
        y_data, x_data = data[y_col], data[x_cols]

        ransac = RANSACRegressor()
        ransac.fit(x_data, y_data)

        inlying_data = data.filter(ransac.inlier_mask_)

        return cls(
            sketch=sketch,
            params=(*ransac.estimator_.coef_, ransac.estimator_.intercept_),
            mask=pl.Series(ransac.inlier_mask_),
            score=abs(ransac.score(inlying_data[x_cols], inlying_data[y_col])),
        )


class Linear2(Linear, arity=2):
    pass


class Linear3(Linear, arity=3):
    pass


class Linear4(Linear, arity=4):
    pass
