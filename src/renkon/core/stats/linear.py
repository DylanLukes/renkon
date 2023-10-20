from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
import polars as pl

from renkon.core.stats.base import Model, Params, Results


@dataclass(frozen=True, kw_only=True, slots=True)
class OLSParams(Params):
    """
    Represents the parameters of an OLS model.
    """

    m: npt.NDArray[np.float64]
    c: np.float64


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
        # todo: cached in the wrong place or?...
        y_col, x_cols = self.model.y_col, self.model.x_cols

        # Calculate the number of observations, parameters, and degrees of freedom.
        self._n = self._data.height
        self._k = len(x_cols) + int(self.model.fit_intercept)
        self._dof = self._n - self._k - 1

        # Calculate the training data residuals.
        y_pred = self.model.predict(self.params)
        self._resid = self._data.select(pl.col(y_col) - y_pred).to_series().to_numpy()

        # Calculate the covariance matrix of the parameters and the standard errors of the parameters.
        rss = self._resid.T @ self._resid

        x = self._data.drop(y_col).to_numpy()
        self._cov_x = rss / self._dof * np.linalg.inv(x.T @ x)
        self._bse = np.sqrt(np.diag(self._cov_x))
        pass

    def __repr__(self) -> str:
        return f"OLSResults(m={list(self.params.m)}, c={self.params.c}, ...)"

    # Implement protocols
    # -------------------

    @property
    def model(self) -> OLSModel:
        return self._model

    @property
    def params(self) -> OLSParams:
        return self._params

    def score(self) -> pl.Expr:
        return self.rsquared(adjust=True)

    # Linear specific properties
    # --------------------------

    @property
    def resid(self) -> npt.NDArray[np.float64]:
        """The residuals of the training data."""
        return self._resid

    @property
    def cov_x(self) -> npt.NDArray[np.float64]:
        """The covariance matrix of the parameters."""
        return self._cov_x

    @property
    def bse(self) -> npt.NDArray[np.float64]:
        """The standard errors of the parameters."""
        return self._bse

    def rsquared(self, *, adjust: bool = True) -> pl.Expr:
        return self.model.rsquared(self.params, adjust=adjust)


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
    def y_col(self) -> str:
        return self._y_col

    @property
    def x_cols(self) -> list[str]:
        return self._x_cols

    @property
    def fit_intercept(self) -> bool:
        return self._fit_intercept

    def fit(self, data: pl.DataFrame) -> OLSResults:
        y_col, x_cols = self.y_col, self.x_cols

        if self._fit_intercept:
            data = data.select(pl.col(y_col), pl.lit(1).alias("const"), pl.col(*x_cols))
            x_cols = ["const", *x_cols]

        # Solve y = mx + c
        (c, *m), _rss, _, _ = np.linalg.lstsq(
            data.select(x_cols),
            data.select(y_col).to_series(),
            rcond=None,
        )

        return OLSResults(_data=data, _model=self, _params=OLSParams(m=np.asarray(m), c=c))

    def predict(self, params: OLSParams) -> pl.Expr:
        y_col, x_cols = self.y_col, self.x_cols

        m, c = params.m, params.c
        return (pl.sum_horizontal([pl.col(x_col) * m_i for x_col, m_i in zip(x_cols, m, strict=True)]) + c).alias(y_col)

    def errors(self, params: OLSParams, *, pred_col: str | None = None) -> pl.Expr:
        pred_expr = pl.col(pred_col) if pred_col else self.predict(params)
        return pl.col(self.y_col) - pred_expr

    def score(self, params: OLSParams, *, err_col: str | None = None) -> pl.Expr:
        return self.rsquared(params, err_col=err_col, adjust=True)

    def rsquared(self, params: OLSParams, *, err_col: str | None = None, adjust: bool = True) -> pl.Expr:
        y_col, x_cols = self.y_col, self.x_cols

        y_pred = pl.col(err_col) if err_col else self.predict(params)
        y_mean = pl.col(y_col).mean().alias("y_mean")

        rss = ((pl.col(y_col) - y_pred) ** 2).sum().alias("rss")
        tss = ((pl.col(y_col) - y_mean) ** 2).sum().alias("tss")
        rsq = (1 - rss / tss).alias("rsq")

        if not adjust:
            return rsq

        n = pl.count().alias("n")
        k = len(x_cols) + int(self._fit_intercept)
        dof = (n - k - 1).alias("dof")
        adj_rsq = (1 - (1 - rsq) * (n - 1) / dof).alias("adj_rsq")
        return adj_rsq


def linear_fit(*, data: pl.DataFrame, y: str, x: list[str] | str) -> tuple[OLSModel, OLSResults]:
    """
    Fit a linear model to the given data.
    """
    x = [x] if isinstance(x, str) else x
    model = OLSModel(y_col=y, x_cols=x)
    return model, model.fit(data)
