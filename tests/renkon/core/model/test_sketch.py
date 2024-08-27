# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import itertools as it

import pytest

import renkon.api as rk
from renkon.core.model import Schema, TraitSketch
from renkon.core.trait import Equal, Linear2


def test_sketch_bindings_missing():
    schema = Schema({"x": rk.int_(), "y": rk.int_()})
    with pytest.raises(ValueError, match="missing in bindings"):
        TraitSketch(spec=Equal.spec, schema=schema, bindings={"A": "x"})


def test_sketch_bindings_extra():
    schema = Schema({"x": rk.int_(), "y": rk.int_()})
    with pytest.raises(ValueError, match="do not occur in pattern"):
        TraitSketch(spec=Equal.spec, schema=schema, bindings={"A": "x", "B": "y", "C": "z"})


def test_sketch_linear2():
    schema = Schema({"time": rk.float_(), "open tabs": rk.float_()})
    TraitSketch(spec=Linear2.spec, schema=schema, bindings={"X": "time", "Y": "open tabs"})


def test_sketch_incorrect_typing():
    schema = Schema({"x": rk.int_(), "name": rk.str_()})
    with pytest.raises(TypeError, match="incompatible type"):
        TraitSketch(spec=Linear2.spec, schema=schema, bindings={"X": "x", "Y": "name"})


def test_sketch_typevars():
    for ty1, ty2 in it.product(rk.equatable().ts, repeat=2):
        schema = Schema({"a": ty1, "b": ty2})
        if ty1 == ty2:
            TraitSketch(spec=Equal.spec, schema=schema, bindings={"A": "a", "B": "b"})
        else:
            with pytest.raises(TypeError):
                TraitSketch(spec=Equal.spec, schema=schema, bindings={"A": "a", "B": "b"})
