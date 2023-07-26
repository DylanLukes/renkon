from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from typing import cast

import numpy as np
import polars as pl

from renkon.stats.models.model import Model, Params, Results


@dataclass(kw_only=True)
class OLSParams(Params):
    """
    Represents the parameters of an OLS model.
    """

    m: list[float]
    c: float

    def __iter__(self) -> Generator[float, None, None]:
        yield from self.m
        yield self.c


@dataclass(kw_only=True)
class OLSResults(Results[OLSParams]):
    _model: OLSModel
    _params: OLSParams

    rss: float
    tss: float
    rsq: float

    @property
    def model(self) -> OLSModel:
        return self._model

    @property
    def params(self) -> OLSParams:
        return self._params

    def score(self, data: pl.DataFrame | None) -> float:
        if data is None:
            return self.rsq

        y_pred = self.predict(data)
        y_true = data[self.model.y_col]

        df = pl.DataFrame({"y_pred": y_pred, "y_true": y_true})

        rsq = (
            df.select(
                rss=((pl.col("y_true") - pl.col("y_pred")) ** 2).sum(),
                tss=((pl.col("y_true") - pl.col("y_true").mean()) ** 2).sum(),
            )
            .select(rsq=1 - pl.col("rss") / pl.col("tss"))
            .item()
        )

        return cast(float, rsq)

    def predict(self, data: pl.DataFrame) -> pl.Series:
        x_cols = self.model.x_cols
        m, c = self.params.m, self.params.c
        return (
            data[self.model.x_cols]
            .select((pl.sum_horizontal(pl.col(x_cols) * pl.lit(m)) + pl.lit(c)).alias(self.model.y_col))
            .to_series()
        )


class OLSModel(Model[OLSParams]):
    """
    Ordinary Least Squares model.

    :param y_col: the name of the dependent variable column.
    :param x_cols: the names of the independent variable columns.
    """

    _x_cols: list[str]
    _y_col: str
    _add_const: bool

    def __init__(self, y_col: str, x_cols: list[str], *, add_const: bool = True):
        if add_const and "const" in x_cols:
            msg = "Cannot add constant column when one already exists."
            raise ValueError(msg)
        self._x_cols = x_cols
        self._y_col = y_col
        self._add_const = add_const

    @property
    def x_cols(self) -> list[str]:
        return self._x_cols

    @property
    def y_col(self) -> str:
        return self._y_col

    def fit(self, data: pl.DataFrame) -> Results[OLSParams]:
        """
        Fit the model to the given data.

        :param data: the data to fit the model to.
        :param add_const: whether to add a constant column to the design matrix.
        """
        y_data = data[self.y_col]
        x_data = data[self.x_cols]
        if self._add_const:
            x_data = x_data.with_columns(const=pl.lit(1))

        # Solve y = mx + c
        (*m, c), rss, _, _ = np.linalg.lstsq(x_data, y_data, rcond=None)

        # Calculate R^2

        tss = y_data.len() * cast(float, y_data.var())
        rsq = 1 - float(rss) / tss

        return OLSResults(_model=self, _params=OLSParams(m=m, c=c), rss=float(rss), tss=tss, rsq=rsq)
