# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import polars as pl
import pytest

from renkon.core.model import type as rk
from renkon.core.model.type import tyconv_pl_to_rk, tyconv_rk_to_pl


def test_convert_polars_type_to_renkon_type():
    assert tyconv_pl_to_rk(pl.Int64) == rk.int_()
    assert tyconv_pl_to_rk(pl.Float64) == rk.float_()
    assert tyconv_pl_to_rk(pl.Utf8) == rk.str_()
    assert tyconv_pl_to_rk(pl.Boolean) == rk.bool_()

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(pl.Date)

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(pl.Time)

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(pl.Datetime)


def test_convert_renkon_type_to_polars_type():
    assert tyconv_rk_to_pl(rk.int_()) == pl.Int64
    assert tyconv_rk_to_pl(rk.float_()) == pl.Float64
    assert tyconv_rk_to_pl(rk.str_()) == pl.Utf8
    assert tyconv_rk_to_pl(rk.bool_()) == pl.Boolean
