# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import operator as op
from abc import ABC
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, ClassVar, Literal, final

from renkon.core.trait import BaseSpecTrait, TraitKind, TraitPattern, TraitResult, TraitSpec
from renkon.core.type import Comparable, Equatable

if TYPE_CHECKING:
    from polars import DataFrame

type _CmpOpStr = Literal["<", "≤", "=", "≥", ">"]
type _CmpLookup[T] = dict[_CmpOpStr, Callable[[T, T], bool]]

_cmp_ops: _CmpLookup[Any] = {
    "<": op.lt,
    "≤": op.le,
    "=": op.eq,
    "≥": op.ge,
    ">": op.gt,
}


class _Compare(BaseSpecTrait, ABC):
    op_str: ClassVar[str]

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, *, op_str: _CmpOpStr, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        cls.op_str = op_str
        cls.base_spec = TraitSpec(
            id=f"{cls.__module__}.{cls.__qualname__}",
            label=f"{cls.__qualname__}",
            kind=TraitKind.LOGICAL,
            pattern=TraitPattern(f"{{A}} {op_str} {{B}}"),
            commutors={"A", "B"},
            typevars={"T": Equatable() if op_str == "=" else Comparable()},
            typings={"A": "T", "B": "T"},
        )

    def infer(self, data: DataFrame, column_bindings: dict[str, str]) -> TraitResult:
        raise NotImplementedError


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


# TODO: special case comparisons between numeric types?
