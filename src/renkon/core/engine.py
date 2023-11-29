from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol

from loguru import logger
from polars import DataFrame

from renkon.core.trait.base import Trait, TraitType
from renkon.core.trait.instantiator import TraitSketchInstantiator


class InferenceEngine(Protocol):
    """
    Core inference engine (protocol) for Renkon.
    """

    @abstractmethod
    def run(self, run_id: str, data: DataFrame) -> Sequence[Trait]:
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
    _results: dict[str, Sequence[Trait]]

    def __init__(self, trait_types: Sequence[TraitType]) -> None:
        self._trait_types = {trait_class.__name__: trait_class for trait_class in trait_types}
        self._results = {}

    def run(self, run_id: str, data: DataFrame) -> Sequence[Trait]:
        # 1. Instantiate the traits on appropriate columns.
        instantiator = TraitSketchInstantiator()
        sketches = instantiator.instantiate(self._trait_types.values(), data.schema)

        traits: list[Trait] = []

        # 2. Run inference strategy for each trait on the data.
        for sketch in sketches:
            logger.info(f"Inferring sketch {sketch}...")
            strategy = sketch.trait_type.inference_strategy()
            trait = strategy.infer(sketch, data)

            traits.append(trait)

        # 3. Store the results.
        self._results[run_id] = traits

        # 4. Return results as promise.
        return traits

    def get_results(self, run_id: str) -> Sequence[Trait]:
        return self._results[run_id]
