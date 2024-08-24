# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Self

from pydantic import BaseModel, model_validator

from renkon.core.model.schema import Schema
from renkon.core.model.trait.spec import TraitSpec


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

    @model_validator(mode="after")
    def check_bindings_keys(self) -> Self:
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
    def check_bindings_values(self) -> Self:
        for mvar, col in self.bindings.items():
            if col not in self.schema.columns:
                msg = f"Cannot bind '{mvar}' to '{col} not found in {list(self.schema.columns)}"
                raise ValueError(msg)
        return self

    # @model_validator(mode="after")
    # def check_bindings_typings(self) -> Self:
    #     for mvar, _ in self.bindings.items():
    #         match self.trait.typings[mvar]:
    #             case RenkonType():
    #                 pass
    #             case str():
    #                 pass
    #     return self
