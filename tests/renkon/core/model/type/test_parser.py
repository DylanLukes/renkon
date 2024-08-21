# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from lark import Lark

from renkon.core.model.type.base import TreeToTypeTransformer, Type
from renkon.core.model.type.parser import grammar


def test_type_parser():
    parser = Lark(grammar, parser="lalr", lexer="standard", transformer=TreeToTypeTransformer())

    assert parser.parse("int") == Type.int()
    assert parser.parse("float") == Type.float()
    assert parser.parse("str") == Type.str()
    assert parser.parse("string") == Type.str()
    assert parser.parse("bool") == Type.bool()
    assert parser.parse("boolean") == Type.bool()
    assert parser.parse("⊥") == Type.bottom()
    assert parser.parse("bottom") == Type.bottom()
    assert parser.parse("int | float") == Type.union(Type.int(), Type.float())
    assert parser.parse("int | float | str") == Type.union(Type.int(), Type.float(), Type.str())
    assert parser.parse("int | (float | str)") == Type.union(Type.int(), Type.float(), Type.str())
    assert parser.parse("⊥ | ⊥") == Type.union()


