# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

__TRAIT_INFO__ = "__trait_info__"

from typing import Annotated

from pydantic import BaseModel, Field

from renkon.core.model.trait.kind import TraitKind
from renkon.core.model.trait.pattern import TraitPattern
from renkon.core.model.type import Type

type TraitId = str


class TraitSpec(BaseModel):
    """
    Model representing the descriptive identity of a trait.

    This is as opposed to the behavioral functionality (e.g. inference, scoring)
    found in :class:`~renkon.core.trait.Trait`.

    >>> trait = TraitSpec.model_validate_json('''{
    ...     "id": "renkon.core.trait.linear.Linear2",
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

    :param id: the unique identifier of the trait.
    :param name: the human-readable name of the trait.
    :param kind: the sort of the trait, e.g. "algebraic", "model", etc.
    :param pattern: the string pattern of the trait
    """

    id: TraitId
    name: str
    kind: TraitKind
    pattern: TraitPattern
    typevars: dict[str, Type] = {}
    typings: dict[str, Annotated[Type | str, Field(union_mode="left_to_right")]] = {}

    @property
    def metavars(self) -> set[str]:
        return set(self.pattern.metavars)

    @property
    def params(self) -> set[str]:
        return set(self.pattern.params)

    # @model_validator(mode="after")
    # def _check_typings_keys_in_pattern(self) -> Self:
    #     for key, _ in self.typings.items():
    #         if key not in self.metavars | self.params:
    #             msg = f"Typing key '{key}' not found in pattern."
    #             raise ValueError(msg)
    #     return self
    #
    # @model_validator(mode="after")
    # def _check_typings_vals_valid_types_or_typevars(self) -> Self:
    #     for key, value in self.typings.items():
    #         if isinstance(value, Type):
    #             continue
    #
    #         if value not in self.typevars:
    #             msg = f"Type variable typing '{value}' for '{key}' not found in typevars."
    #             raise ValueError(msg)
    #     return self
