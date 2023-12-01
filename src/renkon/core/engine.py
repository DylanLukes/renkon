from abc import abstractmethod
from collections.abc import MutableMapping, Sequence
from typing import Any, Protocol

from loguru import logger
from polars import DataFrame

from renkon.core.schema import Schema
from renkon.core.trait import Trait, TraitSketch
from renkon.core.trait.util.instantiate import instantiate_trait

type AnySketch = TraitSketch[Any]

# For now, erase the type parameter from the mapping for results.
type _InferenceResults[T: Trait] = MutableMapping[TraitSketch[T], T | None]
type InferenceResults = _InferenceResults[Any]


class InferenceEngine(Protocol):
    """
    Core inference engine (protocol) for Renkon.
    """

    @abstractmethod
    def run(self, run_id: str, data: DataFrame) -> InferenceResults:
        """
        Run the inference engine.
        @param run_id: the unique ID of this run, used to retrieve results.
        @param data: the data to run on.
        """
        ...

    @abstractmethod
    def get_results(self, run_id: str) -> InferenceResults:
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

    _trait_types: dict[str, type[Trait]]
    _results: dict[str, InferenceResults]

    def __init__(self, trait_types: Sequence[type[Trait]]) -> None:
        self._trait_types = {trait_class.__name__: trait_class for trait_class in trait_types}
        self._results = {}

    def run(self, run_id: str, data: DataFrame) -> InferenceResults:
        schema = Schema.from_polars(data.schema)

        # 1. Instantiate the traits on appropriate columns.
        sketches: list[AnySketch] = []
        for trait_type in self._trait_types.values():
            sketches.extend(instantiate_trait(trait_type, schema))
            for sketch in sketches:
                logger.trace(f"Instantiated {sketch}")

        # 2. Run inference for each trait on the data.
        traits: InferenceResults = {}
        for sketch in sketches:
            logger.trace(f"Starting inference for {sketch}")
            trait_type = sketch.trait_type

            try:
                trait = trait_type.infer(sketch, data)
                traits[sketch] = trait
                logger.trace(f"Inferred {trait}\n")
            except Exception:
                logger.error(f"Error occurred inferring {sketch} (set LOG_LEVEL=DEBUG for details)")
                logger.opt(exception=True).debug("")
                traits[sketch] = None

        # 3. Store the results.
        self._results[run_id] = traits

        # 4. Return results as promise.
        return traits

    def get_results(self, run_id: str) -> InferenceResults:
        return self._results[run_id]
