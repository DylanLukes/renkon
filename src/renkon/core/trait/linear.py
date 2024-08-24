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
        pattern=TraitPattern("{Y} = {a}*{X} + {b}"),
        typings={"X": numeric(), "Y": numeric(), "a": float_(), "b": float_()},
    )
