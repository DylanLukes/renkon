# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import polars as pl
from polars.datatypes import DataType as PolarsDataType

from renkon.core.model import type as rk
from renkon.core.model.type.base import RenkonType


def tyconv_pl_to_rk(pl_ty: PolarsDataType) -> RenkonType:
    """
    Convert a Polars data type to a Renkon data type.
    """
    if pl_ty.is_integer():
        return rk.IntType()

    if pl_ty.is_float():
        return rk.FloatType()

    if pl_ty.is_(pl.String):
        return rk.StringType()

    if pl_ty.is_(pl.Boolean):
        return rk.BoolType()

    msg = f"Unsupported Polars data type: {pl_ty}"
    raise ValueError(msg)


def tyconv_rk_to_pl(rk_ty: RenkonType) -> PolarsDataType:
    """
    Convert a Renkon data type to a Polars data type.
    """

    if rk_ty.is_equal(rk.int_()):
        return pl.Int64()

    if rk_ty.is_equal(rk.float_()) or rk_ty.is_equal(rk.int_() | rk.float_()):
        return pl.Float64()

    if rk_ty.is_equal(rk.str_()):
        return pl.Utf8()

    if rk_ty.is_equal(rk.bool_()):
        return pl.Boolean()

    msg = f"Unsupported Renkon data type: {rk_ty}"
    raise ValueError(msg)
