# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import polars as pl
import pytest

from lark import Lark

from renkon.core.model import type as rkty
from renkon.core.model.type import rk_int, IntType, rk_float, FloatType, rk_str, StringType, rk_bool, BoolType, \
    rk_union, rk_bottom, \
    Type, polars_type_to_renkon_type, renkon_type_to_polars_type, rk_equatable, rk_numeric, rk_comparable
from renkon.core.model.type.base import TreeToType
from renkon.core.model.type.grammar import grammar


# todo: use hypothesis for more robust property-based testing

def test_type_model_dump():
    assert rk_int.model_dump() == "int"
    assert rk_float.model_dump() == "float"
    assert rk_str.model_dump() == "string"
    assert rk_bool.model_dump() == "bool"
    assert rk_union(rk_int, rk_float).model_dump() == "float | int"
    assert rk_union(rk_int, rk_str).model_dump() == "int | string"
    assert rk_bottom.model_dump() == "⊥"
    assert rk_union().model_dump() == "⊥ | ⊥"


def test_type_model_validate():
    assert Type.model_validate("int") == rk_int
    assert Type.model_validate("float") == rk_float
    assert Type.model_validate("string") == rk_str
    assert Type.model_validate("bool") == rk_bool
    assert Type.model_validate("float | int") == rk_union(rk_int, rk_float)
    assert Type.model_validate("int | string") == rk_union(rk_int, rk_str)
    assert Type.model_validate("int | string | float") == rk_union(rk_int, rk_str, rk_float)
    assert Type.model_validate("int | (string | float)") == rk_union(rk_int, rk_str, rk_float)
    assert Type.model_validate("⊥") == rk_bottom
    assert Type.model_validate("⊥ | ⊥") == rk_union()
    assert Type.model_validate("equatable") == rk_equatable
    assert Type.model_validate("comparable") == rk_comparable
    assert Type.model_validate("numeric") == rk_numeric


def test_type_model_validate_json():
    assert Type.model_validate_json(r'"bool"') == rk_bool


def test_primitive_equality():
    assert rk_int == IntType()
    assert rk_float == FloatType()
    assert rk_str == StringType()
    assert rk_bool == BoolType()


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


def test_type_parser():
    parser = Lark(grammar, parser='lalr', lexer="standard", transformer=TreeToType())

    assert parser.parse("int") == rk_int
    assert parser.parse("float") == rk_float
    assert parser.parse("str") == rk_str
    assert parser.parse("string") == rk_str
    assert parser.parse("bool") == rk_bool
    assert parser.parse("boolean") == rk_bool
    assert parser.parse("⊥") == rk_bottom
    assert parser.parse("bottom") == rk_bottom
    assert parser.parse("int | float") == rk_union(rk_int, rk_float)
    assert parser.parse("int | float | str") == rk_union(rk_int, rk_float, rk_str)
    assert parser.parse("int | (float | str)") == rk_union(rk_int, rk_float, rk_str)
    assert parser.parse("⊥ | ⊥") == rk_union()


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
