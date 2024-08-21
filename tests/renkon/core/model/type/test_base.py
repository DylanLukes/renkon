# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from renkon.core.model.type import Type


# TODO: use hypothesis for more robust property-based testing


def test_type_model_dump():
    assert Type.int().model_dump() == "int"
    assert Type.float().model_dump() == "float"
    assert Type.str().model_dump() == "string"
    assert Type.bool().model_dump() == "bool"
    assert Type.union(Type.int(), Type.float()).model_dump() == "float | int"
    assert Type.union(Type.int(), Type.str()).model_dump() == "int | string"
    assert Type.bottom().model_dump() == "⊥"
    assert Type.union().model_dump() == "⊥ | ⊥"


def test_type_model_validate():
    assert Type.model_validate("int") == Type.int()
    assert Type.model_validate("float") == Type.float()
    assert Type.model_validate("string") == Type.str()
    assert Type.model_validate("bool") == Type.bool()
    assert Type.model_validate("float | int") == Type.union(Type.int(), Type.float())
    assert Type.model_validate("int | string") == Type.union(Type.int(), Type.str())
    assert Type.model_validate("int | string | float") == Type.union(Type.int(), Type.str(), Type.float())
    assert Type.model_validate("int | (string | float)") == Type.union(Type.int(), Type.str(), Type.float())
    assert Type.model_validate("⊥") == Type.bottom()
    assert Type.model_validate("⊥ | ⊥") == Type.union()
    assert Type.model_validate("equatable") == Type.equatable()
    assert Type.model_validate("comparable") == Type.comparable()
    assert Type.model_validate("numeric") == Type.numeric()


def test_type_model_validate_json():
    assert Type.model_validate_json(r'"bool"') == Type.bool()


def test_primitive_equality_reflexive():
    assert Type.int() == Type.int()
    assert Type.float() == Type.float()
    assert Type.str() == Type.str()
    assert Type.bool() == Type.bool()


def test_primitive_serialization():
    assert Type.int().model_dump() == "int"
    assert Type.float().model_dump() == "float"
    assert Type.str().model_dump() == "string"
    assert Type.bool().model_dump() == "bool"


def test_primitive_validation():
    assert Type.int().model_validate("int") == Type.int()
    assert Type.float().model_validate("float") == Type.float()
    assert Type.str().model_validate("string") == Type.str()
    assert Type.bool().model_validate("bool") == Type.bool()


def test_union_symmetry():
    assert Type.int() | Type.float() == Type.float() | Type.int()
    assert Type.int() | Type.float() | Type.str() == Type.str() | Type.float() | Type.int()


def test_union_flattening():
    assert (Type.int() | (Type.float() | Type.str())).flatten() == Type.union(Type.int(), Type.float(), Type.str())
    assert ((Type.int() | Type.float()) | Type.str()).flatten() == Type.union(Type.int(), Type.float(), Type.str())
    assert Type.union().flatten() == Type.union()


def test_union_canonicalization():
    assert (Type.int() | (Type.float() | Type.str())).canonicalize() == Type.union(Type.int(), Type.float(), Type.str())
    assert ((Type.int() | Type.float()) | Type.str()).canonicalize() == Type.union(Type.int(), Type.float(), Type.str())
    assert Type.union().canonicalize() == Type.union()


def test_union_normalization():
    assert Type.union(Type.int(), Type.int()).normalize() == Type.int()
    assert Type.union(Type.int(), Type.float()).normalize() == Type.union(Type.int(), Type.float())
    assert (Type.int() | (Type.float() | Type.str())).normalize() == Type.union(Type.int(), Type.float(), Type.str())
    assert ((Type.int() | Type.float()) | Type.str()).normalize() == Type.union(Type.int(), Type.float(), Type.str())
    assert Type.union().normalize() == Type.bottom()


def test_union_equivalence():
    assert Type.union(Type.int(), Type.int()).is_equivalent(Type.int())
    assert Type.union(Type.int(), Type.float()).is_equivalent(Type.union(Type.int(), Type.float()))


def test_union_intersection():
    assert Type.union(Type.int(), Type.float()).intersect(Type.union(Type.int(), Type.str())) == Type.union(Type.int())
    assert Type.union(Type.int(), Type.float()).intersect(Type.union(Type.str(), Type.bool())) == Type.union()


def test_union_dump_python():
    assert Type.union(Type.int(), Type.float()).model_dump() == "float | int"


def test_subtype():
    # Primitive/ Primitive
    assert Type.int().is_subtype(Type.int())
    assert not Type.int().is_subtype(Type.float())

    # Primitive / Union
    assert Type.int().is_subtype(Type.union(Type.int(), Type.float()))
    assert not Type.int().is_subtype(Type.union(Type.float(), Type.str()))

    # Union / Union
    assert Type.union(Type.int(), Type.float()).is_subtype(Type.union(Type.int(), Type.float()))
    assert not Type.union(Type.int(), Type.bool()).is_subtype(Type.union(Type.float(), Type.int()))
    assert Type.union(Type.int(), Type.float()).is_subtype(Type.union(Type.float(), Type.int()))  # symmetry

    # Nested Unions
    assert Type.union(Type.int(), Type.float()).is_subtype(Type.union(Type.int(), Type.union(Type.float(), Type.str())))
    assert not Type.union(Type.int(), Type.bool()).is_subtype(Type.union(Type.int(), Type.union(Type.str(), Type.float())))


def test_numeric():
    assert Type.int().is_numeric()
    assert Type.float().is_numeric()
    assert not Type.str().is_numeric()
    assert not Type.bool().is_numeric()
    assert Type.union(Type.int(), Type.float()).is_numeric()
    assert not Type.union(Type.int(), Type.str()).is_numeric()
    assert not Type.union(Type.str(), Type.bool()).is_numeric()
    assert not Type.union(Type.str(), Type.union(Type.int(), Type.float())).is_numeric()


def test_equatable():
    assert Type.int().is_equatable()
    assert Type.str().is_equatable()
    assert Type.bool().is_equatable()
    assert not Type.float().is_equatable()
    assert Type.union(Type.int(), Type.str()).is_equatable()
    assert not Type.union(Type.int(), Type.float()).is_equatable()
    assert not Type.union(Type.str(), Type.float()).is_equatable()
    assert Type.union(Type.str(), Type.union(Type.int(), Type.bool())).is_equatable()
    assert not Type.union(Type.str(), Type.union(Type.int(), Type.float())).is_equatable()


def test_comparable():
    assert Type.int().is_comparable()
    assert Type.float().is_comparable()
    assert Type.str().is_comparable()
    assert not Type.bool().is_comparable()
    assert Type.union(Type.int(), Type.float()).is_comparable()
    assert Type.union(Type.int(), Type.str()).is_comparable()
    assert Type.union(Type.str(), Type.float()).is_comparable()
    assert Type.union(Type.str(), Type.union(Type.int(), Type.float())).is_comparable()
    assert not Type.union(Type.str(), Type.union(Type.int(), Type.bool())).is_comparable()
    assert not Type.union(Type.str(), Type.union(Type.bool(), Type.float())).is_comparable()
    assert not Type.union(Type.str(), Type.union(Type.bool(), Type.bool())).is_comparable()
