from __future__ import annotations

from typing import Protocol

from polars import DataFrame, Series

from renkon.core.trait.base import Trait, TraitSketch


class InferenceStrategy(Protocol):
    def infer(self, sketch: TraitSketch, data: DataFrame) -> Trait:
        """
        :return: an invariant inferred from the given data.
        """
        raise NotImplementedError

    def test(self, trait: Trait, data: DataFrame) -> Series:
        """
        :param trait: the trait to evaluate.
        :param data: the data to evaluate on (may include the training data, but also test data)
        :return: a boolean series indicating the rows where the trait holds.
        """
        raise NotImplementedError

    def score(self, trait: Trait, data: DataFrame) -> float:
        """
        :param trait: the trait to evaluate.
        :param data: the data to evaluate on (may include the training data, but also test data)
        :return: evaluate the confidence of the inferred trait on the given data.
        """
        raise NotImplementedError
