from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol

from polars import DataFrame

from renkon.core.trait.base import Trait, TraitType
from renkon.core.trait.instantiator import TraitSketchInstantiator


class InferenceEngine(Protocol):
    """
    Core inference engine (protocol) for Renkon.
    """

    @abstractmethod
    def run(self, run_id: str, data: DataFrame) -> None:
        """
        Run the inference engine.
        @param run_id: the unique ID of this run, used to retrieve results.
        @param data: the data to run on.
        """
        ...

    @abstractmethod
    def get_results(self, run_id: str) -> Sequence[Trait]:
        """
        Retrieve the results of a run.
        @param run_id: the unique ID of the run.
        """
        ...


class BatchInferenceEngine(InferenceEngine):
    """
    Simple batch inference engine for Renkon. Does not support any advanced features such as:
      - Task graphs.
      - Dependent inference.
      - Multi-processing.

    Appropriate for small-scale inference, or for testing. Just runs trait inference for a
    given set of traits on a given dataset.
    """

    _trait_types: dict[str, TraitType]

    def __init__(self, trait_types: Sequence[TraitType]) -> None:
        self._trait_types = {trait_class.__name__: trait_class for trait_class in trait_types}

    def run(self, run_id: str, data: DataFrame) -> None:
        # 1. Instantiate the traits on appropriate columns.
        instantiator = TraitSketchInstantiator()
        sketches = instantiator.instantiate(self._trait_types.values(), data.schema)

        print(sketches)

        # 2. Run the inference strategy on the data.
        # 3. Store the results.
        raise NotImplementedError

    def get_results(self, run_id: str) -> Sequence[Trait]:
        raise NotImplementedError
