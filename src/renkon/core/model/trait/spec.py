# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from enum import StrEnum
from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel, Field, model_validator

from renkon.core.model.trait.kind import TraitKind
from renkon.core.model.trait.pattern import TraitPattern
from renkon.core.model.type import RenkonType

type TraitId = str


class TraitSpecState(StrEnum):
    """
    State of the trait in the inference pipeline. As a specification is passed
    through the pipeline, various changes occur until it is in a state suitable
    to feed directly into the inference engine.
    """

    # TODO: implement here


class TraitSpec(BaseModel):
    """
    Model for the descriptive data for a trait, at some point in the inference pipeline.

    This is as opposed to the behavioral functionality (e.g. inference, scoring)
    found in :class:`renkon.core.trait.Trait`. Which behavior to use is specified
    by the id field.

    :param id:        unique identifier of the trait class (fully qualified name)
    :param label:     human-readable label of the trait spec
    :param kind:      sort of the trait, e.g. "algebraic", "model", etc.
    :param pattern:   string pattern of the trait, metavars (for columns) in uppers, inferred params in lowers
    :param commutors: list of sets of metavars that can commute (default: [])
    :param typevars:  declaration of bound type variables for use in typings (default: {})
    :param typings:   declarations of types, may be either Renkon types or typevars (default: {})

    >>> trait = TraitSpec.model_validate_json('''{
    ...     "label": "Linear Regression (2D)",
    ...     "id": "renkon.core.doctest.traits.Linear2",
    ...     "kind": "model",
    ...     "pattern": "{Y} = {a}*{X} + {b}",
    ...     "typings": {
    ...         "X": "numeric",
    ...         "Y": "numeric",
    ...         "a": "float",
    ...         "b": "float"
    ...     }
    ... }''')

    >>> trait = TraitSpec.model_validate(
    ...     {
    ...         "label": "Equal",
    ...         "id": "renkon.core.doctest.traits.Equal",
    ...         "kind": "logical",
    ...         "pattern": "{A} = {B}",
    ...         "commutors": {"A", "B"},
    ...         "typevars": {
    ...             "T": "equatable",
    ...         },
    ...         "typings": {"A": "T", "B": "T"},
    ...     }
    ... )
    """

    label: str
    id: TraitId
    kind: TraitKind
    pattern: TraitPattern
    commutors: set[str] = set()
    typevars: dict[str, RenkonType] = {}
    typings: dict[str, Annotated[RenkonType | str, Field(union_mode="left_to_right")]] = {}

    @property
    def metavars(self) -> set[str]:
        return set(self.pattern.metavars)

    @property
    def params(self) -> set[str]:
        return set(self.pattern.params)

    @model_validator(mode="after")
    def _check_commutors_valid(self) -> Self:
        """Only column metavariables can commute."""

        # Ensure all commutors are valid metavars
        for commutor in self.commutors:
            if commutor not in self.metavars:
                msg = f"Commutor '{commutor}' not found in metavars."
                raise ValueError(msg)

        return self

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
        for key in self.typings:
            if key not in self.metavars | self.params:
                msg = f"Typing key '{key}' not found in pattern."
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_typings_vals_valid_types_or_typevars(self) -> Self:
        for key, value in self.typings.items():
            if isinstance(value, RenkonType):
                continue

            if value not in self.typevars:
                msg = f"Type variable typing '{value}' for '{key}' not found in typevars."
                raise ValueError(msg)
        return self


def _check_valid_instance_trait_spec(spec: TraitSpec):
    if spec.typevars:
        msg = f"Instantiated traits' specs must not contain abstract type variables: {spec.typevars.keys()}"
        raise ValueError(msg)

    tv_tys = {k: ty for k, ty in spec.typings.values() if not isinstance(ty, RenkonType)}
    if tv_tys:
        msg = f"Instantiated traits' typings must refer to Renkon types (not type variables): {tv_tys}"
        raise ValueError(msg)

    return spec

type InstanceTraitSpec = Annotated[TraitSpec, AfterValidator(_check_valid_instance_trait_spec)]