# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import operator as op
from abc import ABC
from collections.abc import Callable
from typing import Any, ClassVar, Literal, final

from renkon.core.model import TraitKind, TraitPattern, TraitSpec
from renkon.core.model.type import comparable, numeric
from renkon.core.trait.base import Trait

type _CmpOpStr = Literal["<", "≤", "=", "≥", ">"]
type _CmpLookup[T] = dict[_CmpOpStr, Callable[[T, T], bool]]

_cmp_ops: _CmpLookup[Any] = {
    "<": op.lt,
    "≤": op.le,
    "=": op.eq,
    "≥": op.ge,
    ">": op.gt,
}


class _Compare(Trait, ABC):
    op_str: ClassVar[str]
    spec: ClassVar[TraitSpec]

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, *, op_str: _CmpOpStr, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        cls.op_str = op_str

        cls.spec = TraitSpec(
            id=f"{cls.__qualname__}",
            name=f"{cls.__name__}",
            kind=TraitKind.LOGICAL,
            pattern=TraitPattern("{A}" f" {op_str} " "{B}"),
            commutors=[{"A", "B"}],
            typevars={"T": numeric() if op_str == "=" else comparable()},
            typings={"A": "T", "B": "T"},
        )


@final
class Equal(_Compare, op_str="="): ...


@final
class Less(_Compare, op_str="<"): ...


@final
class LessOrEqual(_Compare, op_str="≤"): ...


@final
class Greater(_Compare, op_str=">"): ...


@final
class GreaterOrEqual(_Compare, op_str="≥"): ...


if __name__ == "__main__":
    pass
