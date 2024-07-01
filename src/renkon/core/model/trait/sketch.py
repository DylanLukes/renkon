# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Self

from pydantic import BaseModel, model_validator

from renkon.core.model.trait.spec import TraitSpec
from renkon.core.model.type_aliases import ColumnName, ColumnType


class TraitSketchBinding(BaseModel):
    col_name: ColumnName
    col_type: ColumnType


class TraitSketch(BaseModel):
    """
    Represents a sketch of a trait with holes filled.

    :param trait: the trait being sketched.
    :param fills: the assignments of (typed) column names to metavariable in the trait form.
    """

    trait: TraitSpec
    bindings: dict[str, TraitSketchBinding]

    @model_validator(mode="after")
    def check_columns(self) -> Self:
        bound_colnames = set(self.bindings.keys())
        metavars = set(self.trait.pattern.metavariables)
        if bound_colnames != metavars:
            msg = f"Bindings {bound_colnames} do not match trait metavariables {metavars}"
            raise ValueError(msg)
        return self
