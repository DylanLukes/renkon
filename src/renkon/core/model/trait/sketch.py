# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Self

from pydantic import BaseModel, model_validator

from renkon.core.model.schema import Schema
from renkon.core.model.trait.spec import TraitSpec
from renkon.core.model.type import RenkonType


class TraitSketch(BaseModel):
    """
    Represents a sketch of a trait with holes filled.

    :param spec: the trait being sketched.
    :param schema: schema (names -> types) of the data
    :param bindings: bindings (metavariables -> actual column names)
    """

    spec: TraitSpec
    schema: Schema  # pyright: ignore [reportIncompatibleMethodOverride]
    bindings: dict[str, str]

    # Inverted lookup from column name to metavariable
    _bindings_inv: dict[str, str] = {}

    @model_validator(mode="after")
    def _populate_bindings_inv(self) -> Self:
        self._bindings_inv = {v: k for (k, v) in self.bindings.items()}
        return self

    @model_validator(mode="after")
    def _check_bindings_keys(self) -> Self:
        pattern_mvars = set(self.spec.pattern.metavars)
        bound_mvars = set(self.bindings.keys())

        missing_mvars = pattern_mvars - bound_mvars
        extra_mvars = bound_mvars - pattern_mvars

        if len(missing_mvars) > 0:
            msg = f"Metavariables {missing_mvars} are missing in bindings {self.bindings}"
            raise ValueError(msg)

        if len(extra_mvars) > 0:
            msg = f"Metavariables {extra_mvars} do not occur in pattern {self.spec.pattern}"
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def _check_bindings_values(self) -> Self:
        for mvar, col in self.bindings.items():
            if col not in self.schema.columns:
                msg = f"Cannot bind '{mvar}' to '{col} not found in {list(self.schema.columns)}"
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_bindings_typings(self) -> Self:
        # Check that the types in the provided schema match typings.
        for col, ty in self.schema.items():
            metavar = self._bindings_inv[col]
            req_ty = self.spec.typings[metavar]
            match req_ty:
                case RenkonType():
                    if not ty.is_subtype(req_ty):
                        msg = f"Column '{col}' has incompatible type '{ty}', expected '{req_ty}'."
                        raise TypeError(msg)
                case str():
                    raise NotImplementedError

        return self
