from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
import polars as pl
import scipy

from renkon.stats.model import Model, Params, Results


@dataclass(kw_only=True)
class OLSParams(Params):
    """
    Represents the parameters of an OLS model.
    """

    m: npt.NDArray[np.float64]
    c: np.float64

    def __iter__(self) -> Generator[np.float64, None, None]:
        yield from self.m
        yield self.c


@dataclass(kw_only=True)
class OLSResults(Results[OLSParams]):
    """ """

    _data: pl.DataFrame  # TRAINING data used
    _model: OLSModel
    _params: OLSParams

    # Calculated in __post__init__
    _n: int = field(init=False)
    _k: int = field(init=False)
    _dof: int = field(init=False)

    _resid: npt.NDArray[np.float64] = field(init=False)
    _cov_x: npt.NDArray[np.float64] = field(init=False)
    _bse: npt.NDArray[np.float64] = field(init=False)

    def __post_init__(self) -> None:
        # Calculate the number of observations, parameters, and degrees of freedom.
        self._n = self._data.height
        self._k = len(self.model.x_cols) + int(self.model.fit_intercept)
        self._dof = self._n - self._k - 1

        # Calculate the training data residuals.
        y_col, x_cols = self.model.y_col, self.model.x_cols
        y_pred = self.model.predict(self.params)
        self._resid = self._data.select(pl.col(y_col) - y_pred).to_series().to_numpy()

        # Calculate the covariance matrix of the parameters and the standard errors of the parameters.
        rss = self._resid.T @ self._resid

        x = self._data.drop(y_col).to_numpy()
        self._cov_x = rss / self._dof * np.linalg.inv(x.T @ x)
        self._bse = np.sqrt(np.diag(self._cov_x))
        pass

    def __repr__(self):
        return f"OLSResults(m={list(self.params.m)}, c={self.params.c}, ...)"

    @property
    def model(self) -> OLSModel:
        return self._model

    @property
    def params(self) -> OLSParams:
        return self._params

    @property
    def resid(self) -> npt.NDArray[np.float64]:
        """
        The residuals of the training data.
        """
        return self._resid

    @property
    def cov_x(self) -> npt.NDArray[np.float64]:
        """
        The covariance matrix of the parameters.
        """
        return self._cov_x

    @property
    def bse(self) -> npt.NDArray[np.float64]:
        """
        The standard errors of the parameters.
        """
        return self._bse

    def score(self, data: pl.DataFrame | None = None) -> float:
        """
        Score the model on the given data. If ``data`` is ``None``, then the score from the training data is returned.

        :param data: the data to score the model on. Must contain columns named the same as the independent _and_
        dependent variables used to produce these results.
        """
        return data.select(self.rsquared()).item()

    def rsquared(self, adjust: bool = True) -> pl.Expr:
        y_col, x_cols = self.model.y_col, self.model.x_cols

        y_pred = self.model.predict(self.params).alias("y_pred")
        y_mean = pl.col(y_col).mean().alias("y_mean")

        rss = ((pl.col(y_col) - y_pred) ** 2).sum().alias("rss")
        tss = ((pl.col(y_col) - y_mean) ** 2).sum().alias("tss")
        rsq = (1 - rss / tss).alias("rsq")

        if not adjust:
            return rsq

        adj_rsq = (1 - (1 - rsq) * (self._n - 1) / self._dof).alias("adj_rsq")
        return adj_rsq


class OLSModel(Model[OLSParams]):
    """
    Ordinary Least Squares model.

    :param y_col: the name of the dependent variable column.
    :param x_cols: the names of the independent variable columns.
    """

    _x_cols: list[str]
    _y_col: str
    _fit_intercept: bool

    def __init__(self, y_col: str, x_cols: list[str], *, fit_intercept: bool = True):
        if fit_intercept and "const" in x_cols:
            msg = "Cannot add constant column when one already exists."
            raise ValueError(msg)
        self._x_cols = x_cols
        self._y_col = y_col
        self._fit_intercept = fit_intercept

    @property
    def x_cols(self) -> list[str]:
        return self._x_cols

    @property
    def y_col(self) -> str:
        return self._y_col

    @property
    def fit_intercept(self) -> bool:
        return self._fit_intercept

    def fit(self, data: pl.DataFrame) -> OLSResults:
        y_col, x_cols = self.y_col, self.x_cols

        if self._fit_intercept:
            data = data.select(pl.col(y_col), pl.lit(1).alias("const"), pl.col(*x_cols))
            x_cols = ["const", *x_cols]

        # Solve y = mx + c
        (c, *m), rss, _, _ = np.linalg.lstsq(
            data.select(x_cols),
            data.select(y_col).to_series(),
            rcond=None,
        )

        return OLSResults(_data=data, _model=self, _params=OLSParams(m=np.asarray(m), c=c))

    def predict(self, params: OLSParams) -> pl.Expr:
        y_col, x_cols = self.y_col, self.x_cols
        m, c = params.m, params.c
        return pl.sum_horizontal(pl.col(x_cols) * pl.lit(m) + pl.lit(c)).alias(y_col)


def linear_fit(*, data: pl.DataFrame, y: str, x: list[str] | str) -> tuple[OLSModel, OLSResults]:
    """
    Fit a linear model to the given data.
    """
    x = [x] if isinstance(x, str) else x
    model = OLSModel(y_col=y, x_cols=x)
    return model, model.fit(data)
