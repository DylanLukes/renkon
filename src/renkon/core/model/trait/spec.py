# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

__TRAIT_INFO__ = "__trait_info__"

from typing import Annotated, Self

from pydantic import BaseModel, Field, model_validator

from renkon.core.model.trait.kind import TraitKind
from renkon.core.model.trait.pattern import TraitPattern
from renkon.core.model.type import Type

type TraitId = str


class TraitSpec(BaseModel):
    """
    Model for the descriptive data for a trait.

    This is as opposed to the behavioral functionality (e.g. inference, scoring)
    found in :class:`renkon.core.trait.Trait`.

    :param id:        unique identifier of the trait (generally fully-qualified class name)
    :param name:      human-readable name of the trait
    :param kind:      sort of the trait, e.g. "algebraic", "model", etc.
    :param pattern:   string pattern of the trait, metavars (for columns) in uppers, inferred params in lowers
    :param commutors: list of sets of metavars that can commute (default: [])
    :param typevars:  declaration of bound type variables for use in typings (default: {})
    :param typings:   declarations of types, may be either Renkon types or typevars (default: {})

    >>> trait = TraitSpec.model_validate_json('''{
    ...     "id": "renkon.core.doctest.traits.Linear2",
    ...     "name": "Linear Regression (2D)",
    ...     "kind": "model",
    ...     "pattern": "{Y} = {a}*{X} + {b}",
    ...     "typings": {
    ...         "X": "numeric",
    ...         "Y": "numeric",
    ...         "a": "float",
    ...         "b": "float"
    ...     }
    ... }''')

    >>> trait = TraitSpec.model_validate({
    ...     "id": "renkon.core.doctest.traits.Equal",
    ...     "name": "Equal",
    ...     "kind": "logical",
    ...     "pattern": "{A} = {B}",
    ...     "commutors": [{"A", "B"}],
    ...     "typevars": {
    ...         "T": "equatable",
    ...      },
    ...     "typings": {
    ...         "A": "T",
    ...         "B": "T"
    ...     }
    ... })
    """

    id: TraitId
    name: str
    kind: TraitKind
    pattern: TraitPattern
    commutors: list[set[str]] = []
    typevars: dict[str, Type] = {}
    typings: dict[str, Annotated[Type | str, Field(union_mode="left_to_right")]] = {}

    @property
    def metavars(self) -> set[str]:
        return set(self.pattern.metavars)

    @property
    def params(self) -> set[str]:
        return set(self.pattern.params)

    @model_validator(mode="after")
    def _check_all_typed(self) -> Self:
        for metavar in self.metavars:
            if metavar not in self.typings:
                msg = f"Metavariable '{metavar}' from '{self.pattern}' is not typed."
                raise ValueError(msg)

        for param in self.params:
            if param not in self.typings:
                msg = f"Parameter '{param}' from '{self.pattern}' is not typed."
                raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def _check_typings_keys_in_pattern(self) -> Self:
        for key, _ in self.typings.items():
            if key not in self.metavars | self.params:
                msg = f"Typing key '{key}' not found in pattern."
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_typings_vals_valid_types_or_typevars(self) -> Self:
        for key, value in self.typings.items():
            if isinstance(value, Type):
                continue

            if value not in self.typevars:
                msg = f"Type variable typing '{value}' for '{key}' not found in typevars."
                raise ValueError(msg)
        return self
