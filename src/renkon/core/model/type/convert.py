# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import polars as pl

from renkon.core.model.type import rk_int
from renkon.core.model.type.base import Type as RenkonType, rk_float, rk_str, rk_bool


def polars_type_to_renkon_type(rk_ty: pl.PolarsDataType) -> RenkonType:
    """
    Convert a Polars data type to a Renkon data type.
    """
    if rk_ty.is_integer():
        return rk_int

    if rk_ty.is_float():
        return rk_float

    if rk_ty.is_(pl.String):
        return rk_str

    if rk_ty.is_(pl.Boolean):
        return rk_bool

    raise ValueError(f"Unsupported Polars data type: {rk_ty}")


def renkon_type_to_polars_type(rk_ty: RenkonType) -> pl.PolarsDataType:
    """
    Convert a Renkon data type to a Polars data type.
    """

    if rk_ty.is_equal(rk_int):
        return pl.Int64

    if rk_ty.is_equal(rk_float) or rk_ty.is_equal(rk_int | rk_float):
        return pl.Float64

    if rk_ty.is_equal(rk_str):
        return pl.Utf8

    if rk_ty.is_equal(rk_bool):
        return pl.Boolean

    raise ValueError(f"Unsupported Renkon data type: {rk_ty}")
