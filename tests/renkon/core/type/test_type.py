# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import itertools as it

import pytest
from pydantic import TypeAdapter

from renkon.core.type import (
    Bool,
    Bottom,
    Comparable,
    Equatable,
    Float,
    Int,
    Numeric,
    Primitive,
    RenkonType,
    String,
    Top,
    Union,
    is_comparable,
    is_equatable,
    is_numeric,
)
from renkon.core.type._type import COMPARABLE_TYPES, EQUATABLE_TYPES, NUMERIC_TYPES

ta = TypeAdapter(RenkonType)


@pytest.fixture
def primitive_types() -> set[Primitive]:
    return {Int(), Float(), String(), Bool()}


def test_type_model_dump_primitive():
    assert ta.dump_python(Int()) == "int"
    assert ta.dump_python(Float()) == "float"
    assert ta.dump_python(String()) == "string"
    assert ta.dump_python(Bool()) == "bool"


def test_type_model_dump_union():
    assert ta.dump_python(Union(Int(), Float())) == "float | int"
    assert ta.dump_python(Union(Int(), String())) == "int | string"
    assert ta.dump_python(Union()) == "none | none"


def test_type_model_dump_any():
    assert ta.dump_python(Top()) == "any"


def test_type_model_dump_none():
    assert ta.dump_python(Bottom()) == "none"


def test_type_model_validate_instance():
    assert ta.validate_python(Int()) == Int()
    assert ta.validate_python(Float()) == Float()
    assert ta.validate_python(String()) == String()
    assert ta.validate_python(Bool()) == Bool()
    assert ta.validate_python(Union(Int(), Float())) == Union(Int(), Float())
    assert ta.validate_python(Union()) == Union()
    assert ta.validate_python(Bottom()) == Bottom()
    assert ta.validate_python(Top()) == Top()


def test_type_model_validate_primitive():
    assert ta.validate_python("int") == Int()
    assert ta.validate_python("float") == Float()
    assert ta.validate_python("string") == String()
    assert ta.validate_python("bool") == Bool()


def test_type_model_validate_union():
    assert ta.validate_python("float | int") == Union(Int(), Float())
    assert ta.validate_python("int | string") == Union(Int(), String())
    assert ta.validate_python("int | string | float") == Union(Int(), String(), Float())
    assert ta.validate_python("int | (string | float)") == Union(Int(), String(), Float())


def test_type_model_validate_any():
    assert ta.validate_python("any") == Top()
    assert ta.validate_python("⊤") == Top()  # noqa: RUF001
    assert ta.validate_python("⊤ | ⊤") == Union(Top())  # noqa: RUF001


def test_type_model_validate_none():
    assert ta.validate_python("none") == Bottom()
    assert ta.validate_python("⊥") == Bottom()
    assert ta.validate_python("⊥ | ⊥") == Union()


def test_type_model_validate_specials():
    assert ta.validate_python("equatable") == Equatable()
    assert ta.validate_python("comparable") == Comparable()
    assert ta.validate_python("numeric") == Numeric()


def test_type_model_validate_json():
    assert ta.validate_json(r'"bool"') == Bool()
    assert ta.validate_json(r'"int"') == Int()
    assert ta.validate_json(r'"float"') == Float()
    assert ta.validate_json(r'"string"') == String()
    # TODO: write types for validating JSON


def test_primitive_equals_different_instances():
    assert Int() == Int()
    assert Float() == Float()
    assert String() == String()
    assert Bool() == Bool()


def test_primitive_model_dump():
    assert ta.dump_python(Int()) == "int"
    assert ta.dump_python(Float()) == "float"
    assert ta.dump_python(String()) == "string"
    assert ta.dump_python(Bool()) == "bool"


def test_primitive_model_validate():
    assert ta.validate_python("int") == Int()
    assert ta.validate_python("float") == Float()
    assert ta.validate_python("string") == String()
    assert ta.validate_python("bool") == Bool()


def test_union_equals_symmetry():
    assert Int() | Float() == Float() | Int()
    assert Int() | Float() | String() == String() | Float() | Int()


def test_union_flatten():
    assert (Int() | (Float() | String())).flatten() == Union(Int(), Float(), String())
    assert ((Int() | Float()) | String()).flatten() == Union(Int(), Float(), String())
    assert Union().flatten() == Union()


def test_union_canonicalize_empty():
    assert Union().canonicalize() == Union()


def test_union_canonicalize_order_nesting():
    assert (Int() | (Float() | String())).canonicalize() == Union(Int(), Float(), String())
    assert ((Int() | Float()) | String()).canonicalize() == Union(Int(), Float(), String())


def test_union_canonicalize_none():
    assert Union(Bottom()).canonicalize() == Union()
    assert Union(Int(), Bottom()).canonicalize() == Union(Int())


def test_union_canonicalize_any():
    assert Union(Top()).canonicalize() == Union(Top())
    assert Union(Int(), Top()).canonicalize() == Union(Top())


def test_union_normalize_order_nesting():
    assert Union(Int(), Int()).normalize() == Int()
    assert Union(Int(), Float()).normalize() == Union(Int(), Float())
    assert (Int() | (Float() | String())).normalize() == Union(Int(), Float(), String())
    assert ((Int() | Float()) | String()).normalize() == Union(Int(), Float(), String())


def test_union_normalize_none():
    assert Union().normalize() == Bottom()
    assert Union(Bottom()).normalize() == Bottom()


def test_union_normalize_any():
    assert Union(Top()).normalize() == Top()
    assert Union(Int(), Top()).normalize() == Top()


def test_union_is_equivalent():
    assert Union(Int(), Int()).is_equivalent(Int())
    assert Union(Int(), Float()).is_equivalent(Union(Int(), Float()))


def test_union_intersect():
    assert Union(Int(), Float()).intersect(Union(Int(), String())) == Union(Int())
    assert Union(Int(), Float()).intersect(Union(String(), Bool())) == Union()


def test_union_intersect_any():
    assert Union(Top()).intersect(Union(Int(), String())) == Union(Int(), String())


def test_union_dump_python():
    assert ta.dump_python(Union(Int(), Float())) == "float | int"


def test_union_specials_equivalent_and_equal():
    assert Union(EQUATABLE_TYPES).is_equivalent(Equatable())
    assert Union(EQUATABLE_TYPES).is_equal(Equatable())

    assert Union(COMPARABLE_TYPES).is_equivalent(Comparable())
    assert Union(COMPARABLE_TYPES).is_equal(Comparable())

    assert Union(NUMERIC_TYPES).is_equivalent(Numeric())
    assert Union(NUMERIC_TYPES).is_equal(Numeric())


def test_subtype_primitive_reflexive(primitive_types: set[Primitive]):
    for ty1, ty2 in it.product(primitive_types, repeat=2):
        if ty1 == ty2:
            assert ty1.is_subtype(ty2)
            assert ty2.is_subtype(ty1)


def test_subtype_int_float():
    assert Int().is_subtype(Float())


def test_subtype_union():
    # Primitive / Union
    assert Int().is_subtype(Union(Int(), Float()))
    assert not Int().is_subtype(Union(Float(), String()))

    # Union / Union
    assert Union(Int(), Float()).is_subtype(Union(Int(), Float()))
    assert not Union(Int(), Bool()).is_subtype(Union(Float(), Int()))
    assert Union(Int(), Float()).is_subtype(Union(Float(), Int()))  # symmetry

    # Nested Unions
    assert Union(Int(), Float()).is_subtype(Union(Int(), Union(Float(), String())))
    assert not Union(Int(), Bool()).is_subtype(Union(Int(), Union(String(), Float())))


def test_is_numeric():
    assert is_numeric(Int())
    assert is_numeric(Float())
    assert not is_numeric(String())
    assert not is_numeric(Bool())
    assert is_numeric(Union(Int(), Float()))
    assert not is_numeric(Union(Int(), String()))
    assert not is_numeric(Union(String(), Bool()))
    assert not is_numeric(Union(String(), Union(Int(), Float())))


def test_is_equatable():
    assert is_equatable(Int())
    assert is_equatable(String())
    assert is_equatable(Bool())
    assert not is_equatable(Float())
    assert is_equatable(Union(Int(), String()))
    assert not is_equatable(Union(Int(), Float()))
    assert not is_equatable(Union(String(), Float()))
    assert is_equatable(Union(String(), Union(Int(), Bool())))
    assert not is_equatable(Union(String(), Union(Int(), Float())))


def test_is_comparable():
    assert is_comparable(Int())
    assert is_comparable(Float())
    assert is_comparable(String())
    assert not is_comparable(Bool())
    assert is_comparable(Union(Int(), Float()))
    assert is_comparable(Union(Int(), String()))
    assert is_comparable(Union(String(), Float()))
    assert is_comparable(Union(String(), Union(Int(), Float())))
    assert not is_comparable(Union(String(), Union(Int(), Bool())))
    assert not is_comparable(Union(String(), Union(Bool(), Float())))
    assert not is_comparable(Union(String(), Union(Bool(), Bool())))
