"""
Model for uni-variate normal distribution. Has two parameters: mean and standard deviation.

Two versions are provided, one for generating candidates which uses robust estimators (median and MAD)
and one for refined models (where outliers according to the candidates are not in the support) which uses
the mean and standard deviation.
"""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from typing import cast

import polars as pl
import scipy

from renkon.stats.model import Model, Params, Results


@dataclass(kw_only=True)
class NormalParams(Params):
    """
    Represents the parameters of a normal distribution.
    """

    mean: float
    std: float

    def __iter__(self) -> Generator[float, None, None]:
        yield self.mean
        yield self.std


@dataclass(kw_only=True)
class NormalResults(Results[NormalParams]):
    """
    Represents the results of a normal distribution.
    """

    _model: NormalModel
    _params: NormalParams

    @property
    def model(self) -> NormalModel:
        return self._model

    @property
    def params(self) -> NormalParams:
        return self._params

    def score(self, data: pl.DataFrame | None = None) -> float:
        raise NotImplementedError

    def test_inliers(self, data: pl.DataFrame) -> pl.Series:
        raise NotImplementedError


class NormalModel(Model[NormalParams]):
    _x_col: str

    def __init__(self, col: str):
        self._x_col = col

    @property
    def x_cols(self) -> list[str]:
        return [self._x_col]

    @property
    def y_col(self) -> None:
        return None

    def fit(self, data: pl.DataFrame) -> NormalResults:
        x = data[self._x_col]
        mean = pl.mean(x)
        std = cast(float, pl.std(x))

        return NormalResults(_model=self, _params=NormalParams(mean=mean, std=std))


class RobustNormalModel(NormalModel):
    """
    Like NormalModel, but uses robust estimators (median and adjusted MAD) instead of mean
    and standard deviation. Can be used to generate candidates in the presence of outliers.
    """

    def fit(self, data: pl.DataFrame) -> NormalResults:
        x = data[self._x_col]
        median = pl.mean(x)
        mad_adj = scipy.stats.median_abs_deviation(x, scale="normal")
        return NormalResults(_model=self, _params=NormalParams(mean=median, std=mad_adj))
