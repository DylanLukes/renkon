from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import polars as pl

    from renkon.core.stats.base.model import Model
    from renkon.core.stats.base.params import ModelParams


class ModelResults[P: ModelParams](Protocol):
    """
    Represents the results of a model. Can be used to predict values
    for new data, or to evaluate the model's score on new data.

    For convenience, it offers a few delegate methods to the underlying model.
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

    # Convenience Delegate Methods
    # ----------------------------

    def predict(self, params: P | None = None) -> pl.Expr:
        """
        Convenience method delegating to :meth:`~renkon.models.model.Model.predict`.

        Predict the dependent variable for the given data.

        :param data: the data to predict the dependent variable for.
        :param params: the parameters to use for the prediction, or ``None`` to use the model's parameters.
        """
        return self.model.predict_expr(params or self.params)

    def errors(self, params: P | None = None) -> pl.Expr:
        """
        Convenience method delegating to :meth:`~renkon.models.model.Model.errors`.

        Calculate the errors/residuals for the given data.

        :param data: the data to calculate the errors/residuals for.
        :param params: the parameters to use for the prediction, or ``None`` to use the model's parameters.
        """
        return self.model.errors_expr(params or self.params)

    def score(self, params: P | None = None) -> pl.Expr:
        """
        :return: an expression that evaluates to the (float, [0,1]) score of the model.
        """
        return self.model.score_expr(params or self.params)
