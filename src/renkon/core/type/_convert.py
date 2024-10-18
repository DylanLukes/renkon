# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import polars as pl
from polars import datatypes as pldt

from renkon.core.type import _type as rkty
from renkon.core.type._type import RenkonType


def tyconv_pl_to_rk(pl_ty: pldt.DataType) -> RenkonType:
    """
    Convert a Polars data type to a Renkon data type.
    """
    if pl_ty.is_integer():
        return rkty.Int()

    if pl_ty.is_float():
        return rkty.Float()

    if pl_ty.is_(pl.String):
        return rkty.String()

    if pl_ty.is_(pl.Boolean):
        return rkty.Bool()

    msg = f"Unsupported Polars data type: {pl_ty}"
    raise ValueError(msg)


def tyconv_rk_to_pl(rk_ty: RenkonType) -> pldt.DataType:
    """
    Convert a Renkon data type to a Polars data type.
    """

    if rk_ty.is_equal(rkty.Int()):
        return pl.Int64()

    if rk_ty.is_equal(rkty.Float()) or rk_ty.is_equal(rkty.Int() | rkty.Float()):
        return pl.Float64()

    if rk_ty.is_equal(rkty.String()):
        return pl.Utf8()

    if rk_ty.is_equal(rkty.Bool()):
        return pl.Boolean()

    msg = f"Unsupported Renkon data type: {rk_ty}"
    raise ValueError(msg)
