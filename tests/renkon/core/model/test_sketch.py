# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest

import renkon.api as rk
from renkon.core.model import TraitSketch, Schema
from renkon.core.trait import Linear2, Equal


def test_sketch_bindings_missing():
    schema = Schema({
        "x": rk.int_(),
        "y": rk.int_()
    })
    with pytest.raises(ValueError, match="missing in bindings"):
        TraitSketch(
            spec=Equal.spec,
            schema=schema,
            bindings={
                "A": "x"
            }
        )


def test_sketch_bindings_extra():
    schema = Schema({
        "x": rk.int_(),
        "y": rk.int_()
    })
    with pytest.raises(ValueError, match="do not occur in pattern"):
        TraitSketch(
            spec=Equal.spec,
            schema=schema,
            bindings={
                "A": "x",
                "B": "y",
                "C": "z"
            }
        )


def test_sketch_linear2():
    schema = Schema({
        "time": rk.float_(),
        "open tabs": rk.float_()
    })
    TraitSketch(
        spec=Linear2.spec,
        schema=schema,
        bindings={
            "X": "time",
            "Y": "open tabs"
        }
    )