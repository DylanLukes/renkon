# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import itertools as it

import pytest

from renkon.core import type as rkty
from renkon.core.schema import Schema
from renkon.core.trait import Equal, Linear2, TraitSketch
from renkon.core.type import RenkonType


def test_sketch_bindings_missing():
    schema = Schema({"x": rkty.Int(), "y": rkty.Int()})
    with pytest.raises(ValueError, match="missing in bindings"):
        TraitSketch(spec=Equal.base_spec, schema=schema, bindings={"A": "x"})


def test_sketch_bindings_extra():
    schema = Schema({"x": rkty.Int(), "y": rkty.Int()})
    with pytest.raises(ValueError, match="do not occur in pattern"):
        TraitSketch(spec=Equal.base_spec, schema=schema, bindings={"A": "x", "B": "y", "C": "z"})


def test_sketch_linear2():
    schema = Schema({"time": rkty.Float(), "open tabs": rkty.Float()})
    TraitSketch(spec=Linear2.base_spec, schema=schema, bindings={"X_1": "time", "Y": "open tabs"})


def test_sketch_incorrect_typing():
    schema = Schema({"x": rkty.Int(), "name": rkty.String()})
    with pytest.raises(TypeError, match="incompatible type .* does not satisfy bound"):
        TraitSketch(spec=Linear2.base_spec, schema=schema, bindings={"X_1": "x", "Y": "name"})


def test_sketch_typevar_incorrect_typing():
    schema = Schema({"a": rkty.Float(), "b": rkty.Float()})
    with pytest.raises(TypeError, match="incompatible type .* does not satisfy bound .* of typevar"):
        TraitSketch(spec=Equal.base_spec, schema=schema, bindings={"A": "a", "B": "b"})


def test_sketch_typevar_instantiation():
    for ty1, ty2 in it.product(rkty.Union(*RenkonType.equatable_types()).ts, repeat=2):
        schema = Schema({"a": ty1, "b": ty2})
        if ty1 == ty2:
            TraitSketch(spec=Equal.base_spec, schema=schema, bindings={"A": "a", "B": "b"})
        else:
            with pytest.raises(TypeError, match=r"Could not instantiate .* given concrete .*"):
                TraitSketch(spec=Equal.base_spec, schema=schema, bindings={"A": "a", "B": "b"})
