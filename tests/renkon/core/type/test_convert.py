# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import pytest
from polars import datatypes as plty

from renkon.core import type as rkty
from renkon.core.type import tyconv_pl_to_rk, tyconv_rk_to_pl


def test_convert_polars_type_to_renkon_type():
    assert tyconv_pl_to_rk(plty.Int64()) == rkty.Int()
    assert tyconv_pl_to_rk(plty.Float64()) == rkty.Float()
    assert tyconv_pl_to_rk(plty.Utf8()) == rkty.String()
    assert tyconv_pl_to_rk(plty.Boolean()) == rkty.Bool()

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(plty.Date())

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(plty.Time())

    with pytest.raises(ValueError, match="Unsupported Polars data type"):
        tyconv_pl_to_rk(plty.Datetime())


def test_convert_renkon_type_to_polars_type():
    assert tyconv_rk_to_pl(rkty.Int()) == plty.Int64
    assert tyconv_rk_to_pl(rkty.Float()) == plty.Float64
    assert tyconv_rk_to_pl(rkty.String()) == plty.Utf8
    assert tyconv_rk_to_pl(rkty.Bool()) == plty.Boolean
