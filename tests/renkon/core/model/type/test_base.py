# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from renkon.core.model.type import Type, int_, float_, str_, bool_, union, bottom, equatable, comparable, numeric


# TODO: use hypothesis for more robust property-based testing


def test_type_model_dump():
    assert int_().model_dump() == "int"
    assert float_().model_dump() == "float"
    assert str_().model_dump() == "string"
    assert bool_().model_dump() == "bool"
    assert union(int_(), float_()).model_dump() == "float | int"
    assert union(int_(), str_()).model_dump() == "int | string"
    assert bottom().model_dump() == "⊥"
    assert union().model_dump() == "⊥ | ⊥"


def test_type_model_validate():
    assert Type.model_validate("int") == int_()
    assert Type.model_validate("float") == float_()
    assert Type.model_validate("string") == str_()
    assert Type.model_validate("bool") == bool_()
    assert Type.model_validate("float | int") == union(int_(), float_())
    assert Type.model_validate("int | string") == union(int_(), str_())
    assert Type.model_validate("int | string | float") == union(int_(), str_(), float_())
    assert Type.model_validate("int | (string | float)") == union(int_(), str_(), float_())
    assert Type.model_validate("⊥") == bottom()
    assert Type.model_validate("⊥ | ⊥") == union()
    assert Type.model_validate("equatable") == equatable()
    assert Type.model_validate("comparable") == comparable()
    assert Type.model_validate("numeric") == numeric()


def test_type_model_validate_json():
    assert Type.model_validate_json(r'"bool"') == bool_()


def test_primitive_equality_reflexive():
    assert int_() == int_()
    assert float_() == float_()
    assert str_() == str_()
    assert bool_() == bool_()


def test_primitive_serialization():
    assert int_().model_dump() == "int"
    assert float_().model_dump() == "float"
    assert str_().model_dump() == "string"
    assert bool_().model_dump() == "bool"


def test_primitive_validation():
    assert int_().model_validate("int") == int_()
    assert float_().model_validate("float") == float_()
    assert str_().model_validate("string") == str_()
    assert bool_().model_validate("bool") == bool_()


def test_union_symmetry():
    assert int_() | float_() == float_() | int_()
    assert int_() | float_() | str_() == str_() | float_() | int_()


def test_union_flattening():
    assert (int_() | (float_() | str_())).flatten() == union(int_(), float_(), str_())
    assert ((int_() | float_()) | str_()).flatten() == union(int_(), float_(), str_())
    assert union().flatten() == union()


def test_union_canonicalization():
    assert (int_() | (float_() | str_())).canonicalize() == union(int_(), float_(), str_())
    assert ((int_() | float_()) | str_()).canonicalize() == union(int_(), float_(), str_())
    assert union().canonicalize() == union()


def test_union_normalization():
    assert union(int_(), int_()).normalize() == int_()
    assert union(int_(), float_()).normalize() == union(int_(), float_())
    assert (int_() | (float_() | str_())).normalize() == union(int_(), float_(), str_())
    assert ((int_() | float_()) | str_()).normalize() == union(int_(), float_(), str_())
    assert union().normalize() == bottom()


def test_union_equivalence():
    assert union(int_(), int_()).is_equivalent(int_())
    assert union(int_(), float_()).is_equivalent(union(int_(), float_()))


def test_union_intersection():
    assert union(int_(), float_()).intersect(union(int_(), str_())) == union(int_())
    assert union(int_(), float_()).intersect(union(str_(), bool_())) == union()


def test_union_dump_python():
    assert union(int_(), float_()).model_dump() == "float | int"


def test_subtype():
    # Primitive/ Primitive
    assert int_().is_subtype(int_())
    assert not int_().is_subtype(float_())

    # Primitive / Union
    assert int_().is_subtype(union(int_(), float_()))
    assert not int_().is_subtype(union(float_(), str_()))

    # Union / Union
    assert union(int_(), float_()).is_subtype(union(int_(), float_()))
    assert not union(int_(), bool_()).is_subtype(union(float_(), int_()))
    assert union(int_(), float_()).is_subtype(union(float_(), int_()))  # symmetry

    # Nested Unions
    assert union(int_(), float_()).is_subtype(union(int_(), union(float_(), str_())))
    assert not union(int_(), bool_()).is_subtype(union(int_(), union(str_(), float_())))


def test_numeric():
    assert int_().is_numeric()
    assert float_().is_numeric()
    assert not str_().is_numeric()
    assert not bool_().is_numeric()
    assert union(int_(), float_()).is_numeric()
    assert not union(int_(), str_()).is_numeric()
    assert not union(str_(), bool_()).is_numeric()
    assert not union(str_(), union(int_(), float_())).is_numeric()


def test_equatable():
    assert int_().is_equatable()
    assert str_().is_equatable()
    assert bool_().is_equatable()
    assert not float_().is_equatable()
    assert union(int_(), str_()).is_equatable()
    assert not union(int_(), float_()).is_equatable()
    assert not union(str_(), float_()).is_equatable()
    assert union(str_(), union(int_(), bool_())).is_equatable()
    assert not union(str_(), union(int_(), float_())).is_equatable()


def test_comparable():
    assert int_().is_comparable()
    assert float_().is_comparable()
    assert str_().is_comparable()
    assert not bool_().is_comparable()
    assert union(int_(), float_()).is_comparable()
    assert union(int_(), str_()).is_comparable()
    assert union(str_(), float_()).is_comparable()
    assert union(str_(), union(int_(), float_())).is_comparable()
    assert not union(str_(), union(int_(), bool_())).is_comparable()
    assert not union(str_(), union(bool_(), float_())).is_comparable()
    assert not union(str_(), union(bool_(), bool_())).is_comparable()
