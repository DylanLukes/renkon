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
    def score(self, data: pl.DataFrame | None = None) -> float:
        """
        Score the fit of the model on the given data, or on the training data if
        ``data`` is ``None``.

        :param data: the data to score the model on, or ``None`` to score on the training data.
        :return: a score in the range [0, 1].
        """
        ...

    @abstractmethod
    def predict(self, data: pl.DataFrame) -> pl.Series:
        """
        Predict the dependent variable for the given data.

        Convenience method that calls :meth:`~renkon.models.model.Model.predict`.
        """
        ...


class Model(Protocol[_ParamsT_co]):
    """
    Represents a statistical model, prior to fitting.
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
    def y_col(self) -> str:
        """
        :return: the name of the dependent variable column.
        """
        ...

    @abstractmethod
    def fit(self: Model[_ParamsT], data: pl.DataFrame) -> Results[_ParamsT]:
        """
        :param data: the data to fit the model to.
        :return: the :class:`~renkon.models.model.Results` of fitting the model to the given data.
        """
        ...
