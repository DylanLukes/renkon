# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from pydantic import BaseModel

from renkon.core.model.sketch import SketchInfo
from renkon.core.model.trait.new import TraitScore
from renkon.core.model.util.bitseries import BitSeries


class TraitResult(BaseModel):
    """
    Model representing a single trait inference result.
    """

    sketch: SketchInfo
    score: TraitScore
    match_mask: BitSeries
