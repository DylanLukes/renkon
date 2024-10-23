# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
__all__ = [
    "BaseSpecTrait",
    "Trait",
    "TraitId",
    "TraitKind",
    "TraitPattern",
    "TraitResult",
    "TraitScore",
    "TraitSketch",
    "TraitSpec",
]

from renkon.core.trait._kind import TraitKind
from renkon.core.trait._pattern import TraitPattern
from renkon.core.trait._result import TraitResult, TraitScore
from renkon.core.trait._sketch import TraitSketch
from renkon.core.trait._spec import TraitId, TraitSpec
from renkon.core.trait._trait import BaseSpecTrait, Trait
