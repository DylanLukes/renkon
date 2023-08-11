from __future__ import annotations

from abc import abstractmethod
from collections.abc import Generator
from typing import Any, Protocol, TypeVar

import polars as pl

_ParamsT = TypeVar("_ParamsT", bound="Params")
_ParamsT_co = TypeVar("_ParamsT_co", bound="Params", covariant=True)
_ParamsT_contra = TypeVar("_ParamsT_contra", bound="Params", contravariant=True)


class Params(Protocol):
    def __iter__(self) -> Generator[Any, None, None]:
        ...


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
    def score(self, data: pl.DataFrame) -> float:
        """
        Score the fit of the model on the given data.

        :param data: the data to score the model on, or ``None`` to score on the training data.
        :return: a score in the range [0, 1].
        """
        ...


class Model(Protocol[_ParamsT_co]):
    """
    Represents a statistical model, prior to fitting.

    This is a somewhat loose/broad notion of "model" which can include things like
    a normal distribution, or a linear regression, or a clustering algorithm.

    A linear regression, which can be used to predict a dependent variable from
    independent variables, would also implement SupportsPredict.
    """

    @property
    @abstractmethod
    def x_cols(self) -> list[str]:
        """
        :return: the names of the independent variable columns.
        """
        ...

    @property
    @abstractmethod
    def y_col(self) -> str | None:
        """
        :return: the name of the dependent variable column, if any.
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
        Predict the dependent variable for the given data.

        Convenience method that calls :meth:`~renkon.models.model.Model.predict`.

        :param data: the data to predict the dependent variable for.
        :param params: the parameters to use for the prediction, or ``None`` to use the model's parameters.
        """
        ...
