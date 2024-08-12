# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from renkon.core.model.dtypes import rk_int, Int, rk_float, Float, rk_str, String, rk_bool, Bool, rk_union, rk_bottom


# todo: use hypothesis for more robust property-based testing

def test_primitive_equality():
    assert rk_int == Int()
    assert rk_float == Float()
    assert rk_str == String()
    assert rk_bool == Bool()


def test_primitive_serialization():
    assert rk_int.model_dump() == "int"
    assert rk_float.model_dump() == "float"
    assert rk_str.model_dump() == "string"
    assert rk_bool.model_dump() == "bool"


def test_primitive_validation():
    assert rk_int.model_validate("int") == rk_int
    assert rk_float.model_validate("float") == rk_float
    assert rk_str.model_validate("string") == rk_str
    assert rk_bool.model_validate("bool") == rk_bool


def test_union_symmetry():
    assert rk_int | rk_float == rk_float | rk_int
    assert rk_int | rk_float | rk_str == rk_str | rk_float | rk_int


def test_union_flattening():
    assert (rk_int | (rk_float | rk_str)).flatten() == rk_union(rk_int, rk_float, rk_str)
    assert ((rk_int | rk_float) | rk_str).flatten() == rk_union(rk_int, rk_float, rk_str)
    assert rk_union().flatten() == rk_union()


def test_union_canonicalization():
    assert (rk_int | (rk_float | rk_str)).canonicalize() == rk_union(rk_int, rk_float, rk_str)
    assert ((rk_int | rk_float) | rk_str).canonicalize() == rk_union(rk_int, rk_float, rk_str)
    assert rk_union().canonicalize() == rk_union()


def test_union_normalization():
    assert rk_union(rk_int, rk_int).normalize() == rk_int
    assert rk_union(rk_int, rk_float).normalize() == rk_union(rk_int, rk_float)
    assert (rk_int | (rk_float | rk_str)).normalize() == rk_union(rk_int, rk_float, rk_str)
    assert ((rk_int | rk_float) | rk_str).normalize() == rk_union(rk_int, rk_float, rk_str)
    assert rk_union().normalize() == rk_bottom


def test_union_equivalence():
    assert rk_union(rk_int, rk_int).is_equivalent(rk_int)
    assert rk_union(rk_int, rk_float).is_equivalent(rk_union(rk_int, rk_float))


def test_union_intersection():
    assert rk_union(rk_int, rk_float).intersect(rk_union(rk_int, rk_str)) == rk_union(rk_int)
    assert rk_union(rk_int, rk_float).intersect(rk_union(rk_str, rk_bool)) == rk_union()


def test_union_dump_python():
    assert rk_union(rk_int, rk_float).model_dump() == "float | int"


def test_subtype():
    # Primitive/ Primitive
    assert rk_int.is_subtype(rk_int)
    assert not rk_int.is_subtype(rk_float)

    # Primitive / Union
    assert rk_int.is_subtype(rk_union(rk_int, rk_float))
    assert not rk_int.is_subtype(rk_union(rk_float, rk_str))

    # Union / Union
    assert rk_union(rk_int, rk_float).is_subtype(rk_union(rk_int, rk_float))
    assert not rk_union(rk_int, rk_bool).is_subtype(rk_union(rk_float, rk_int))
    assert rk_union(rk_int, rk_float).is_subtype(rk_union(rk_float, rk_int))  # symmetry

    # Nested Unions
    assert rk_union(rk_int, rk_float).is_subtype(rk_union(rk_int, rk_union(rk_float, rk_str)))
    assert not rk_union(rk_int, rk_bool).is_subtype(rk_union(rk_int, rk_union(rk_str, rk_float)))


def test_numeric():
    assert rk_int.is_numeric()
    assert rk_float.is_numeric()
    assert not rk_str.is_numeric()
    assert not rk_bool.is_numeric()
    assert rk_union(rk_int, rk_float).is_numeric()
    assert not rk_union(rk_int, rk_str).is_numeric()
    assert not rk_union(rk_str, rk_bool).is_numeric()
    assert not rk_union(rk_str, rk_union(rk_int, rk_float)).is_numeric()


def test_equatable():
    assert rk_int.is_equatable()
    assert rk_str.is_equatable()
    assert rk_bool.is_equatable()
    assert not rk_float.is_equatable()
    assert rk_union(rk_int, rk_str).is_equatable()
    assert not rk_union(rk_int, rk_float).is_equatable()
    assert not rk_union(rk_str, rk_float).is_equatable()
    assert rk_union(rk_str, rk_union(rk_int, rk_bool)).is_equatable()
    assert not rk_union(rk_str, rk_union(rk_int, rk_float)).is_equatable()


def test_comparable():
    assert rk_int.is_comparable()
    assert rk_float.is_comparable()
    assert rk_str.is_comparable()
    assert not rk_bool.is_comparable()
    assert rk_union(rk_int, rk_float).is_comparable()
    assert rk_union(rk_int, rk_str).is_comparable()
    assert rk_union(rk_str, rk_float).is_comparable()
    assert rk_union(rk_str, rk_union(rk_int, rk_float)).is_comparable()
    assert not rk_union(rk_str, rk_union(rk_int, rk_bool)).is_comparable()
    assert not rk_union(rk_str, rk_union(rk_bool, rk_float)).is_comparable()
    assert not rk_union(rk_str, rk_union(rk_bool, rk_bool)).is_comparable()
