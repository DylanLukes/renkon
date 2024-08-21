# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import polars as pl
import pytest

from renkon.core.model import type as rkty
from renkon.core.model.type import tyconv_pl_to_rk, tyconv_rk_to_pl


def test_convert_polars_type_to_renkon_type():
    assert tyconv_pl_to_rk(pl.Int64) == rkty.Type.int()
    assert tyconv_pl_to_rk(pl.Float64) == rkty.Type.float()
    assert tyconv_pl_to_rk(pl.Utf8) == rkty.Type.str()
    assert tyconv_pl_to_rk(pl.Boolean) == rkty.Type.bool()

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(pl.Date)

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(pl.Time)

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(pl.Datetime)


def test_convert_renkon_type_to_polars_type():
    assert tyconv_rk_to_pl(rkty.Type.int()) == pl.Int64
    assert tyconv_rk_to_pl(rkty.Type.float()) == pl.Float64
    assert tyconv_rk_to_pl(rkty.Type.str()) == pl.Utf8
    assert tyconv_rk_to_pl(rkty.Type.bool()) == pl.Boolean
