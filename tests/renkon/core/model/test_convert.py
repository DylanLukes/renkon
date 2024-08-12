# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import polars as pl
import pytest

import renkon.core.model.type as rkty
from renkon.core.model.type import polars_type_to_renkon_type, renkon_type_to_polars_type


def test_polars_type_to_renkon_type():
    assert polars_type_to_renkon_type(pl.Int64) == rkty.rk_int
    assert polars_type_to_renkon_type(pl.Float64) == rkty.rk_float
    assert polars_type_to_renkon_type(pl.Utf8) == rkty.rk_str
    assert polars_type_to_renkon_type(pl.Boolean) == rkty.rk_bool

    with pytest.raises(ValueError):
        polars_type_to_renkon_type(pl.Date)
        polars_type_to_renkon_type(pl.Time)
        polars_type_to_renkon_type(pl.Datetime)


def test_renkon_type_to_polars_type():
    assert renkon_type_to_polars_type(rkty.rk_int) == pl.Int64
    assert renkon_type_to_polars_type(rkty.rk_float) == pl.Float64
    assert renkon_type_to_polars_type(rkty.rk_str) == pl.Utf8
    assert renkon_type_to_polars_type(rkty.rk_bool) == pl.Boolean