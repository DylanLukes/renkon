from lark import Lark, LarkError

grammar = r"""
    ?start: type

    type: paren
        | union
        | top
        | bottom
        | special
        | primitive

    paren: "(" type ")"

    union: type "|" type -> union

    primitive: "int" -> int
        | "integer" -> int
        | "float" -> float
        | "str" -> string
        | "string" -> string
        | "bool" -> bool
        | "boolean" -> bool

    special: "equatable" -> equatable
        | "comparable" -> comparable
        | "numeric" -> numeric

    top: "⊤" -> top
        | "top" -> top
        | "any" -> top

    bottom: "⊥" -> bottom
        | "bottom" -> bottom
        | "none" -> bottom


    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, lexer="standard", parser="lalr")
