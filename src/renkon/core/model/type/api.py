# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from renkon.core.model.type.base import (
    BoolType,
    BottomType,
    FloatType,
    IntType,
    RenkonType,
    StringType,
    TopType,
    UnionType,
)


def int_() -> IntType:
    return IntType()


def float_() -> FloatType:
    return FloatType()


def str_() -> StringType:
    return StringType()


def bool_() -> BoolType:
    return BoolType()


def top() -> TopType:
    return TopType()


any_ = top


def bottom() -> BottomType:
    return BottomType()


none = bottom


def union(*types: RenkonType) -> UnionType:
    return UnionType(*types).canonicalize()


def equatable() -> UnionType:
    return union(int_(), str_(), bool_())


def comparable() -> UnionType:
    return union(int_(), float_(), str_())


def numeric() -> UnionType:
    return union(int_(), float_())
