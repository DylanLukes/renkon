# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import polars as pl

from renkon.core.model import type as rk


def tyconv_pl_to_rk(pl_ty: pl.PolarsDataType) -> rk.RenkonType:
    """
    Convert a Polars data type to a Renkon data type.
    """
    if pl_ty.is_integer():
        return rk.int_()

    if pl_ty.is_float():
        return rk.float_()

    if pl_ty.is_(pl.String):
        return rk.str_()

    if pl_ty.is_(pl.Boolean):
        return rk.bool_()

    msg = f"Unsupported Polars data type: {pl_ty}"
    raise ValueError(msg)


def tyconv_rk_to_pl(rk_ty: rk.RenkonType) -> pl.PolarsDataType:
    """
    Convert a Renkon data type to a Polars data type.
    """

    if rk_ty.is_equal(rk.int_()):
        return pl.Int64

    if rk_ty.is_equal(rk.float_()) or rk_ty.is_equal(rk.int_() | rk.float_()):
        return pl.Float64

    if rk_ty.is_equal(rk.str_()):
        return pl.Utf8

    if rk_ty.is_equal(rk.bool_()):
        return pl.Boolean

    msg = f"Unsupported Renkon data type: {rk_ty}"
    raise ValueError(msg)
