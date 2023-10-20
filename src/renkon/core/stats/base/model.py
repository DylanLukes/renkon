from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

import polars as pl

if TYPE_CHECKING:
    from renkon.core.stats.base.params import Params
    from renkon.core.stats.base.results import Results


class Model[P: Params](Protocol):
    """
    Represents a (predictive) statistical model, prior to fitting.

    This is a somewhat loose/broad notion of "model" which can include things like
    a normal distribution, or a linear regression, or a clustering algorithm.

    A linear regression, which can be used to predict a dependent variable from
    independent variables, would also implement SupportsPredict.

    @note Based loosely on statsmodels.base.model.
    """

    @property
    @abstractmethod
    def y_col(self) -> str:
        """
        :return: the name of the dependent variable column.
        """
        ...

    @property
    @abstractmethod
    def x_cols(self) -> list[str]:
        """
        :return: the names of the independent variable columns.
        """
        ...

    @abstractmethod
    def fit(self, data: pl.DataFrame) -> Results[P]:
        """
        Fit (or more generally "train", "learn") the model on the given data.

        :param data: the data to fit the model to.
        :return: the :class:`~renkon.models.model.Results` of fitting the model to the given data.
        """
        ...

    @abstractmethod
    def predict(self, params: P) -> pl.Expr:
        """
        Expression: predicted y values.

        :param params: the parameters to use for the prediction.
        :return: an expression that evaluates to the predicted dependent variable.
        """
        ...

    @abstractmethod
    def errors(self, params: P, *, pred_col: str | None = None) -> pl.Expr:
        """
        Expression: errors/residuals (has default implementation).

        If you already have the predicted values, you can pass their column name. Otherwise,
        a self.predict(params) term will be used.

        :param params: the parameters to use for the prediction.
        :param pred_col: the name of the column containing the predicted values, or ``None`` to use the default.
        :return: an expression that evaluates to the errors/residuals of the prediction.
        """
        pred_expr = pl.col(pred_col) if pred_col else self.predict(params)
        return pred_expr - pl.col(self.y_col)

    @abstractmethod
    def score(self, params: P, *, err_col: str | None = None) -> pl.Expr:
        """
        Expression: Calculate the score of the model on the data.

        :param params: the parameters to use for the prediction.
        :param err_col: the errors/residuals of the prediction, or ``None`` to calculate them.
        :return: an expression that evaluates to the score of the model.
        """
        ...
