# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from renkon.core.model import TraitKind, TraitPattern, TraitSpec
from renkon.core.model.type import float_, numeric
from renkon.core.trait.base import Trait


class Linear2(Trait):
    spec = TraitSpec(
        id=f"{__qualname__}",
        name=f"{__name__}",
        kind=TraitKind.MODEL,
        pattern=TraitPattern("{Y} = {b_1}*{X_1} + {b_0}"),
        typings={"X_1": numeric(), "Y": numeric(), **{b: float_() for b in ("b_0", "b_1")}},
    )


class Linear3(Trait):
    spec = TraitSpec(
        id=f"{__qualname__}",
        name=f"{__name__}",
        kind=TraitKind.MODEL,
        pattern=TraitPattern("{Y} = {b_2}*{X_2} + {b_1}*{X_1} + {b_0}"),
        typings={"X_2": numeric(), "X_1": numeric(), "Y": numeric(), **{b: float_() for b in ("b_0", "b_1", "b_2")}},
    )
