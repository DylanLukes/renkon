# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import itertools as it

import pytest

from renkon.core.type import Bool, Bottom, Float, Int, Primitive, RenkonType, String, Top, Union


@pytest.fixture
def primitive_types() -> set[Primitive]:
    return {Int(), Float(), String(), Bool()}


def test_type_model_dump_primitive():
    assert Int().model_dump() == "int"
    assert Float().model_dump() == "float"
    assert String().model_dump() == "string"
    assert Bool().model_dump() == "bool"


def test_type_model_dump_union():
    assert Union(Int(), Float()).model_dump() == "float | int"
    assert Union(Int(), String()).model_dump() == "int | string"
    assert Union().model_dump() == "none | none"


def test_type_model_dump_any():
    assert Top().model_dump() == "any"


def test_type_model_dump_none():
    assert Bottom().model_dump() == "none"


def test_type_model_validate_primitive():
    assert RenkonType.model_validate("int") == Int()
    assert RenkonType.model_validate("float") == Float()
    assert RenkonType.model_validate("string") == String()
    assert RenkonType.model_validate("bool") == Bool()


def test_type_model_validate_union():
    assert RenkonType.model_validate("float | int") == Union(Int(), Float())
    assert RenkonType.model_validate("int | string") == Union(Int(), String())
    assert RenkonType.model_validate("int | string | float") == Union(Int(), String(), Float())
    assert RenkonType.model_validate("int | (string | float)") == Union(Int(), String(), Float())


def test_type_model_validate_any():
    assert RenkonType.model_validate("any") == Top()
    assert RenkonType.model_validate("⊤") == Top()  # noqa: RUF001
    assert RenkonType.model_validate("⊤ | ⊤") == Union(Top())  # noqa: RUF001


def test_type_model_validate_none():
    assert RenkonType.model_validate("none") == Bottom()
    assert RenkonType.model_validate("⊥") == Bottom()
    assert RenkonType.model_validate("⊥ | ⊥") == Union()


def test_type_model_validate_specials():
    assert RenkonType.model_validate("equatable") == Union(*RenkonType.equatable_types())
    assert RenkonType.model_validate("comparable") == Union(*RenkonType.comparable_types())
    assert RenkonType.model_validate("numeric") == Union(*RenkonType.numeric_types())


def test_type_model_validate_json():
    assert RenkonType.model_validate_json(r'"bool"') == Bool()
    assert RenkonType.model_validate_json(r'"int"') == Int()
    assert RenkonType.model_validate_json(r'"float"') == Float()
    assert RenkonType.model_validate_json(r'"string"') == String()
    # TODO: write types for validating JSON


def test_primitive_equals_different_instances():
    assert Int() == Int()
    assert Float() == Float()
    assert String() == String()
    assert Bool() == Bool()


def test_primitive_model_dump():
    assert Int().model_dump() == "int"
    assert Float().model_dump() == "float"
    assert String().model_dump() == "string"
    assert Bool().model_dump() == "bool"


def test_primitive_model_validate():
    assert Int().model_validate("int") == Int()
    assert Float().model_validate("float") == Float()
    assert String().model_validate("string") == String()
    assert Bool().model_validate("bool") == Bool()


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
    assert Union(Int(), Float()).model_dump() == "float | int"


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
    assert Int().is_numeric()
    assert Float().is_numeric()
    assert not String().is_numeric()
    assert not Bool().is_numeric()
    assert Union(Int(), Float()).is_numeric()
    assert not Union(Int(), String()).is_numeric()
    assert not Union(String(), Bool()).is_numeric()
    assert not Union(String(), Union(Int(), Float())).is_numeric()


def test_is_equatable():
    assert Int().is_equatable()
    assert String().is_equatable()
    assert Bool().is_equatable()
    assert not Float().is_equatable()
    assert Union(Int(), String()).is_equatable()
    assert not Union(Int(), Float()).is_equatable()
    assert not Union(String(), Float()).is_equatable()
    assert Union(String(), Union(Int(), Bool())).is_equatable()
    assert not Union(String(), Union(Int(), Float())).is_equatable()


def test_is_comparable():
    assert Int().is_comparable()
    assert Float().is_comparable()
    assert String().is_comparable()
    assert not Bool().is_comparable()
    assert Union(Int(), Float()).is_comparable()
    assert Union(Int(), String()).is_comparable()
    assert Union(String(), Float()).is_comparable()
    assert Union(String(), Union(Int(), Float())).is_comparable()
    assert not Union(String(), Union(Int(), Bool())).is_comparable()
    assert not Union(String(), Union(Bool(), Float())).is_comparable()
    assert not Union(String(), Union(Bool(), Bool())).is_comparable()
