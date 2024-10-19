# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
"""
Unary traits related to refining the "type" of a column beyond what is included in the
dataframe schema. For example, a column of type float might actually (almost) always consist
of just integers.

Refinements in a Renkon sense are a stronger concept than predicates, as they quantify the
conformance of the column's data. For example, _how close_ to being integral.
"""

from abc import ABC
from typing import ClassVar, final

from polars import DataFrame
from pydantic import TypeAdapter

from renkon.core.trait import BaseSpecTrait, TraitKind, TraitPattern, TraitSpec
from renkon.core.trait._trait import TraitResult
from renkon.core.type import RenkonType


class _Refinement(BaseSpecTrait, ABC):
    refines: ClassVar[RenkonType]

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, *, base_type: RenkonType | str, **kwargs: None):
        if not isinstance(base_type, RenkonType):
            base_type = TypeAdapter(RenkonType).validate_python(base_type)

        cls.base_spec = TraitSpec(
            id=f"{cls.__name__}",
            label=f"{cls.__qualname__}",
            kind=TraitKind.REFINEMENT,
            pattern=TraitPattern("{X}: " f"{base_type}/{cls.__name__}"),
            typings={"X": base_type},
        )


@final
class NonNull(_Refinement, base_type="any"):
    def infer(self, data: DataFrame, column_bindings: dict[str, str]) -> TraitResult:
        raise NotImplementedError


@final
class NonNegative(_Refinement, base_type="numeric"):
    def infer(self, data: DataFrame, column_bindings: dict[str, str]) -> TraitResult:
        raise NotImplementedError


@final
class NonZero(_Refinement, base_type="numeric"):
    def infer(self, data: DataFrame, column_bindings: dict[str, str]) -> TraitResult:
        raise NotImplementedError


@final
class Integral(_Refinement, base_type="float"):
    def infer(self, data: DataFrame, column_bindings: dict[str, str]) -> TraitResult:
        raise NotImplementedError
