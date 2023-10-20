from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

import polars as pl

if TYPE_CHECKING:
    from renkon.core.stats.base.model import Model
    from renkon.core.stats.base.params import Params


class Results[P: Params](Protocol):
    """
    Represents the results of a model. Can be used to predict values
    for new data, or to evaluate the model's score on new data.
    """

    @property
    @abstractmethod
    def model(self) -> Model[P]:
        """
        :return: the model that generated these results.
        """
        ...

    @property
    @abstractmethod
    def params(self) -> P:
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

    def predict(self, params: P | None = None) -> pl.Expr:
        """
        Convenience method delegating to :meth:`~renkon.models.model.Model.predict`.

        Predict the dependent variable for the given data.

        :param data: the data to predict the dependent variable for.
        :param params: the parameters to use for the prediction, or ``None`` to use the model's parameters.
        """
        return self.model.predict(params or self.params)

    def errors(self, params: P | None = None) -> pl.Expr:
        """
        Convenience method delegating to :meth:`~renkon.models.model.Model.errors`.

        Calculate the errors/residuals for the given data.

        :param data: the data to calculate the errors/residuals for.
        :param params: the parameters to use for the prediction, or ``None`` to use the model's parameters.
        """
        return self.model.errors(params or self.params)
