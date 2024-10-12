# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from renkon.core.type import Bool, Bottom, Float, Int, String, Union, parser


def test_type_parser():
    assert parser.parse("int") == Int()
    assert parser.parse("float") == Float()
    assert parser.parse("str") == String()
    assert parser.parse("string") == String()
    assert parser.parse("bool") == Bool()
    assert parser.parse("boolean") == Bool()
    assert parser.parse("⊥") == Bottom()
    assert parser.parse("bottom") == Bottom()
    assert parser.parse("int | float") == Union(Int(), Float())
    assert parser.parse("int | float | str") == Union(Int(), Float(), String())
    assert parser.parse("int | (float | str)") == Union(Int(), Float(), String())
    assert parser.parse("⊥ | ⊥") == Union()
