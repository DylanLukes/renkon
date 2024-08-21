# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import polars as pl

from renkon.core.model.type.base import Type as RenkonType


def tyconv_pl_to_rk(pl_ty: pl.PolarsDataType) -> RenkonType:
    """
    Convert a Polars data type to a Renkon data type.
    """
    if pl_ty.is_integer():
        return RenkonType.int()

    if pl_ty.is_float():
        return RenkonType.float()

    if pl_ty.is_(pl.String):
        return RenkonType.str()

    if pl_ty.is_(pl.Boolean):
        return RenkonType.bool()

    msg = f"Unsupported Polars data type: {pl_ty}"
    raise ValueError(msg)


def tyconv_rk_to_pl(rk_ty: RenkonType) -> pl.PolarsDataType:
    """
    Convert a Renkon data type to a Polars data type.
    """

    if rk_ty.is_equal(RenkonType.int()):
        return pl.Int64

    if rk_ty.is_equal(RenkonType.float()) or rk_ty.is_equal(RenkonType.int() | RenkonType.float()):
        return pl.Float64

    if rk_ty.is_equal(RenkonType.str()):
        return pl.Utf8

    if rk_ty.is_equal(RenkonType.bool()):
        return pl.Boolean

    msg = f"Unsupported Renkon data type: {rk_ty}"
    raise ValueError(msg)
