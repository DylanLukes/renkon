from __future__ import annotations

from typing import Protocol

from polars import DataFrame

from renkon.core.trait.base import Trait, TraitSketch


class InferenceStrategy[T: Trait](Protocol):
    def infer(self, sketch: TraitSketch[T], data: DataFrame) -> T:
        """
        :return: an invariant inferred from the given data.
        """
        ...

    def score(self, data: DataFrame) -> float:
        """
        :param trait: the trait to evaluate.
        :param data: the data to evaluate on (may include the training data, but also test data)
        :return: evaluate the confidence of the inferred trait on the given data.
        """
        ...
