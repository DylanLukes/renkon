from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
import polars as pl
import scipy

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
    """
    :param _x_train: the X (independent) data used to generate the model.
    :param _y_train: the Y (dependent) data used to generate the model.
    :param _model: the model used to generate the results.
    :param _params: the fit parameters of the model.

    :param _k: the number of parameters (including the constant if used).
    :param _dof: the degrees of freedom.
    :param _cov_x: the covariance matrix of the parameters.

    :param _n_train: the number of observations in the training data.
    :param _rss_train: the residual sum of squares over the training data.
    :param _tss_train: the total sum of squares over the training data.
    :param _rsq_train: the R-squared over the training data.
    :param _rsq_adj_train: the adjusted R-squared over the training data.
    """

    _x_train: pl.DataFrame
    _y_train: pl.Series
    _model: OLSModel
    _params: OLSParams

    # Calculated in __post__init__
    _k: int = field(init=False)
    _dof: int = field(init=False)
    _cov_x: npt.NDArray[np.float64] = field(init=False)
    _bse: npt.NDArray[np.float64] = field(init=False)

    # Calculated in __post__init__, specific to the training data.
    _n_train: int = field(init=False)
    _rss_train: float = field(init=False)
    _tss_train: float = field(init=False)
    _rsq_train: float = field(init=False)
    _rsq_adj_train: float = field(init=False)

    def __post_init__(self) -> None:
        if self._x_train.height != self._y_train.len():
            msg = "The number of rows in the X and Y data must be the same."
            raise ValueError(msg)

        # Calculate the number of observations, parameters, and degrees of freedom.
        self._n = self._x_train.height
        self._k = len(self.model.x_cols) + int(self.model.fit_intercept)
        self._dof = self._n - self._k - 1

        # Calculate the residual sum of squares (RSS), total sum of squares (TSS), and R-squared (R^2)
        # over the _training data_. This is done here so that the values are cached.
        self._rsq_train, self._rsq_adj_train, self._rss_train, self._tss_train = self._rsquared(
            self._y_train, self._x_train
        )

        # Calculate the covariance matrix of the design matrix (Cov(X)), and the standard errors of the parameters.
        x = self._x_train.to_numpy()
        self._cov_x = self._rss_train / self._dof * np.linalg.inv(x.T @ x)
        self._bse = np.sqrt(np.diag(self._cov_x))

    @property
    def model(self) -> OLSModel:
        return self._model

    @property
    def params(self) -> OLSParams:
        return self._params

    @property
    def bse(self) -> npt.NDArray[np.float64]:
        """
        :returns: the standard errors of the fitted parameters.
        """
        return self._bse

    def score(self, data: pl.DataFrame | None = None) -> float:
        """
        Score the model on the given data. If ``data`` is ``None``, then the score from the training data is returned.

        :param data: the data to score the model on. Must contain columns named the same as the independent _and_
        dependent variables used to produce these results.
        """
        if data is None:
            return self._rsq_adj_train
        _, adj_rsq, _, _ = self._rsquared(data[self.model.y_col], data[self.model.x_cols])
        return adj_rsq

    def predict(self, data: pl.DataFrame) -> pl.Series:
        """
        Predict the dependent variable using the given data.

        :param data: the data to predict the dependent variable on. Must contain columns named the same as the
        independent variables used to produce these results.
        """
        x_cols = self.model.x_cols
        m, c = self.params.m, self.params.c
        return (
            data[self.model.x_cols]
            .select((pl.sum_horizontal(pl.col(x_cols) * pl.lit(m)) + pl.lit(c)).alias(self.model.y_col))
            .to_series()
        )

    def _rsquared(self, y_data: pl.Series, x_data: pl.DataFrame) -> tuple[float, float, float, float]:
        """
        :returns: a tuple of the R-squared, adjusted R-squared, residual sum of squares, and total sum of squares.
        """
        y_pred = self.predict(x_data).to_numpy()
        y_true = y_data.to_numpy()

        # Calculate the residual sum of squares (RSS) and total sum of squares (TSS).
        rss = np.sum((y_true - y_pred) ** 2)
        tss = np.sum((y_true - np.mean(y_true)) ** 2)

        # Calculate the R-squared and adjusted R-squared.
        n = x_data.height
        k = self._k
        rsq = 1 - rss / tss
        adj_rsq = 1 - (1 - rsq) * (n - 1) / (n - k - 1)

        return rsq, adj_rsq, rss, tss

    def _confidence_interval(
        self,
        pct: float = 0.95,
    ) -> tuple[OLSParams, OLSParams]:
        """
        Return a tuple of the lower and upper bounds of the ``pct`` % confidence interval.
        :param pct: the confidence interval percentage (default 95%).
        """
        pass

        # Calculate the T-score for the degrees of freedom.
        alpha = 1 - pct
        n = self._n_train
        k = self._k
        dof = n - k - 1
        _t = scipy.stats.t.ppf(1 - alpha / 2, dof)

        # Extract the standard errors of the estimated parameters from Cov(X).
        *se_m, se_c = self.bse

        # Calculate the lower and upper bounds of the confidence interval.
        lower = OLSParams(
            m=self.params.m - _t * se_m,
            c=self.params.c - _t * se_c,
        )

        upper = OLSParams(
            m=self.params.m + _t * se_m,
            c=self.params.c + _t * se_c,
        )

        return lower, upper


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
        """
        Fit the model to the given data.

        :param data: the data to fit the model to.
        :param add_const: whether to add a constant column to the design matrix.
        """
        y_data = data[self.y_col]
        x_data = data[self.x_cols]
        if self._fit_intercept:
            x_data = x_data.with_columns(_const_=pl.lit(1)).select("_const_", *self.x_cols)

        # Solve y = mx + c
        (c, *m), rss, _, _ = np.linalg.lstsq(x_data, y_data, rcond=None)

        return OLSResults(_x_train=x_data, _y_train=y_data, _model=self, _params=OLSParams(m=m, c=c))
