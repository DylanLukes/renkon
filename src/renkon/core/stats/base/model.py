from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, TypeVar

import polars as pl

from renkon.core.stats.base.params import Params

_ParamsT = TypeVar("_ParamsT", bound="Params")
_ParamsT_co = TypeVar("_ParamsT_co", bound="Params", covariant=True)
_ParamsT_contra = TypeVar("_ParamsT_contra", bound="Params", contravariant=True)


class Results(Protocol[_ParamsT_co]):
    """
    Represents the results of a model. Can be used to predict values
    for new data, or to evaluate the model's score on new data.
    """

    @property
    @abstractmethod
    def model(self) -> Model[_ParamsT_co]:
        """
        :return: the model that generated these results.
        """
        ...

    @property
    @abstractmethod
    def params(self) -> _ParamsT_co:
        """
        :return: the parameters used to generate these results.
        """
        ...

    @abstractmethod
    def score(self) -> pl.Expr:
        """
        :return: an expression that evaluates to the (float, [0,1]) score of the model.
        """
        ...

    # Convenience Delegate Methods
    # ----------------------------

    def predict(self: Results[_ParamsT], params: _ParamsT | None = None) -> pl.Expr:
        """
        Convenience method delegating to :meth:`~renkon.models.model.Model.predict`.

        Predict the dependent variable for the given data.

        :param data: the data to predict the dependent variable for.
        :param params: the parameters to use for the prediction, or ``None`` to use the model's parameters.
        """
        return self.model.predict(params or self.params)

    def errors(self: Results[_ParamsT], params: _ParamsT | None = None) -> pl.Expr:
        """
        Convenience method delegating to :meth:`~renkon.models.model.Model.errors`.

        Calculate the errors/residuals for the given data.

        :param data: the data to calculate the errors/residuals for.
        :param params: the parameters to use for the prediction, or ``None`` to use the model's parameters.
        """
        return self.model.errors(params or self.params)


class Model(Protocol[_ParamsT_co]):
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
    def fit(self: Model[_ParamsT], data: pl.DataFrame) -> Results[_ParamsT]:
        """
        Fit (or more generally "train", "learn") the model on the given data.

        :param data: the data to fit the model to.
        :return: the :class:`~renkon.models.model.Results` of fitting the model to the given data.
        """
        ...

    @abstractmethod
    def predict(self: Model[_ParamsT], params: _ParamsT) -> pl.Expr:
        """
        Expression: predicted y values.

        :param params: the parameters to use for the prediction.
        :return: an expression that evaluates to the predicted dependent variable.
        """
        ...

    @abstractmethod
    def errors(self: Model[_ParamsT], params: _ParamsT, *, pred_col: str | None = None) -> pl.Expr:
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
    def score(self: Model[_ParamsT], params: _ParamsT, *, err_col: str | None = None) -> pl.Expr:
        """
        Expression: Calculate the score of the model on the data.

        :param params: the parameters to use for the prediction.
        :param err_col: the errors/residuals of the prediction, or ``None`` to calculate them.
        :return: an expression that evaluates to the score of the model.
        """
        ...