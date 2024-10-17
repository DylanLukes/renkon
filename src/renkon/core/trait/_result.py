# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Annotated, Any

from annotated_types import Gt, Lt
from pydantic import BaseModel

from renkon._internal.bitseries import BitSeries
from renkon.core.schema import Schema
from renkon.core.trait._spec import TraitSpec

type TraitScore = Annotated[float, Gt(0.0), Lt(1.0)]


class TraitResult(BaseModel):
    """
    Model representing a single trait inference result.
    """

    spec: TraitSpec
    schema: Schema
    bindings: dict[str, str]

    score: TraitScore
    match_mask: BitSeries

    params: dict[str, tuple[str, Any]]
