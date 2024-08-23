# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from lark import Lark

from renkon.core.model import type as rk
from renkon.core.model.type.base import TreeToTypeTransformer
from renkon.core.model.type.parser import grammar


def test_type_parser():
    parser = Lark(grammar, parser="lalr", lexer="standard", transformer=TreeToTypeTransformer())

    assert parser.parse("int") == rk.int_()
    assert parser.parse("float") == rk.float_()
    assert parser.parse("str") == rk.str_()
    assert parser.parse("string") == rk.str_()
    assert parser.parse("bool") == rk.bool_()
    assert parser.parse("boolean") == rk.bool_()
    assert parser.parse("⊥") == rk.none()
    assert parser.parse("bottom") == rk.none()
    assert parser.parse("int | float") == rk.union(rk.int_(), rk.float_())
    assert parser.parse("int | float | str") == rk.union(rk.int_(), rk.float_(), rk.str_())
    assert parser.parse("int | (float | str)") == rk.union(rk.int_(), rk.float_(), rk.str_())
    assert parser.parse("⊥ | ⊥") == rk.union()


