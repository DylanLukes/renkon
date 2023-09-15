from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, TypeVar

from polars import DataFrame, Series

from renkon.core.stats.base.model import Model
from renkon.core.stats.sampling import Sampler

_ModelT = TypeVar("_ModelT", bound=Model[Any])
_ModelT_co = TypeVar("_ModelT_co", bound=Model[Any], covariant=True)
_ModelT_contra = TypeVar("_ModelT_contra", bound=Model[Any], contravariant=True)


class GenerationPhase(Protocol[_ModelT]):
    """
    Represents a minimal-sample model generation phase of a sample consensus process.
    """

    @abstractmethod
    def generate(self, data: DataFrame, sample: Series) -> _ModelT:
        """
        Generate a model from the given sample of the data.
        :param data: the data to generate the model from.
        :param sample: the sample of the data to generate the model from.
        :return: a model generated from the given sample of the data.
        """
        ...

    @abstractmethod
    def check_generated_model(self, data: DataFrame, model: _ModelT) -> bool:
        """
        Check whether the given model is desirable. This can be overriden
        for specific problems to bail out early if the model parameters are not desirable.

        :param model: the model to check.
        :param data: the data to check the model on.
        :return: whether the given model should be kept (true) or discarded.
        """
        ...


class VerificationPhase(Protocol[_ModelT_co]):
    """
    Represents a verification phase for a generated model.

    Goal is to check whether the given model is "interesting" (likely to gather large support) and non-degenerate.
    """

    def verify(self, data: DataFrame, model: _ModelT) -> bool:
        """
        Check whether the model is likely interesting, i.e. likely to gather large support.

        This allows us to bail out early if the model is not interesting (unlikely to gather large support).

        :param data: the data to check the model on (only a subset need be used).
        :param model: the model to check.
        :return: whether the model is likely interesting and should be refined.
        """
        ...


class RefinementPhase(Protocol[_ModelT]):
    """
    Represents a refinement phase for a generated model. Note that the refined model may be the same as the
    generated model, but may also be a different model. For example, when fitting a normal distribution, the
    generated models may use robust estimators (median and MAD) while the refined model may use mean/stddev,
    on the assumption that the outliers have been mostly removed.
    """

    def refine(self, data: DataFrame, model: _ModelT) -> _ModelT:
        """
        Refine the given model.

        :param data: the data to refine the model on (only a subset need be used).
        :param model: the model to refine.
        :return: the refined model.
        """
        ...


class SampleConsensusProcess(Protocol[_ModelT]):
    @property
    @abstractmethod
    def sampling_phase(self) -> Sampler:
        ...

    @property
    @abstractmethod
    def generation_phase(self) -> GenerationPhase[_ModelT]:
        ...

    @property
    @abstractmethod
    def check_phase(self) -> VerificationPhase[_ModelT]:
        ...

    @property
    @abstractmethod
    def refinement_phase(self) -> RefinementPhase[_ModelT]:
        ...
