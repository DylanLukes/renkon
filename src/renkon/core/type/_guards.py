# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import TypeGuard

from renkon.core.type._type import (
    Bool,
    Comparable,
    Equatable,
    Float,
    Int,
    Numeric,
    Primitive,
    RenkonType,
    String,
    Union,
)


def is_concrete(ty: RenkonType) -> bool:
    return isinstance(ty, Primitive)


def is_union_of_concrete(ty: RenkonType) -> TypeGuard[Union]:
    return is_union(ty) and all(is_concrete(m) for m in ty.members)


def is_abstract(ty: RenkonType) -> bool:
    return not is_concrete(ty)


def is_int(ty: RenkonType) -> TypeGuard[Int]:
    return isinstance(ty, Int)


def is_float(ty: RenkonType) -> TypeGuard[Float]:
    return isinstance(ty, Float)


def is_str(ty: RenkonType) -> TypeGuard[String]:
    return isinstance(ty, String)


def is_bool(ty: RenkonType) -> TypeGuard[Bool]:
    return isinstance(ty, Bool)


def is_union(ty: RenkonType) -> TypeGuard[Union]:
    return isinstance(ty, Union)


def is_numeric(ty: RenkonType) -> bool:
    return ty.is_subtype(Numeric())


def is_equatable(ty: RenkonType) -> bool:
    return ty.is_subtype(Equatable())


def is_comparable(ty: RenkonType) -> bool:
    return ty.is_subtype(Comparable())
