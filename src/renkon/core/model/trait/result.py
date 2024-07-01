# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Annotated

from annotated_types import Gt, Lt
from pydantic import BaseModel

from renkon.core.model.bitseries import BitSeries
from renkon.core.model.trait.sketch import TraitSketch

type TraitResultScore = Annotated[float, Gt(0.0), Lt(1.0)]


class TraitResult(BaseModel):
    """
    Model representing a single trait inference result.
    """

    sketch: TraitSketch
    score: TraitResultScore
    match_mask: BitSeries
