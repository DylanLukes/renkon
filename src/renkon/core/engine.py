from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol

from polars import DataFrame

from renkon.core.trait.base import Trait, TraitType


class Engine(Protocol):
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


class SimpleEngine(Engine):
    """
    Simple inference engine for Renkon. Does not support any advanced features such as:
      - Task graphs.
      - Dependent inference.
      - Multi-processing.

    Appropriate for small-scale inference, or for testing.
    """

    _trait_types: dict[str, TraitType]

    def __init__(self, trait_types: Sequence[TraitType]) -> None:
        self._trait_types = {trait_class.__name__: trait_class for trait_class in trait_types}

    def run(self, run_id: str, data: DataFrame) -> None:
        # 1. Instantiate the traits on appropriate columns.
        # 2. Run the inference strategy on the data.
        # 3. Store the results.
        raise NotImplementedError

    def _sketch_trait(self, trait_type: TraitType, _data: DataFrame) -> Trait:
        for _arity in trait_type.arities():
            pass
        raise NotImplementedError

    def get_results(self, run_id: str) -> Sequence[Trait]:
        raise NotImplementedError
