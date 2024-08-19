# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Self

from pydantic import BaseModel, model_validator

from renkon.core.model.trait.spec import TraitSpec
from renkon.core.model.type_aliases import ColumnName, ColumnType


class TraitSketch(BaseModel):
    """
    Represents a sketch of a trait with holes filled.

    :param trait: the trait being sketched.
    :param metavar_bindings: the assignments of (typed) column names to metavariable in the trait form.
    """

    trait: TraitSpec
    metavar_bindings: dict[str, tuple[ColumnName, ColumnType]]

    @model_validator(mode="after")
    def check_columns(self) -> Self:
        bound_colnames = set(self.metavar_bindings.keys())
        metavars = set(self.trait.pattern.metavars)
        if bound_colnames != metavars:
            msg = f"Bindings {bound_colnames} do not match trait metavariables {metavars}"
            raise ValueError(msg)
        return self
