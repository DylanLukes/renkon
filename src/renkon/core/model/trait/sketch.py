# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from pydantic import BaseModel

from renkon.core.model import Schema
from renkon.core.model.trait import TraitSpec


class TraitSketch(BaseModel):
    """
    Represents a sketch of a trait with holes filled.

    :param trait: the trait being sketched.
    :param fills: the assignments of (typed) column names to metavariable in the trait form.
    """
    trait: TraitSpec
    fills: Schema
