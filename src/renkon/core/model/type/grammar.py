grammar = r"""
    ?start: type

    type: paren
        | union
        | prim
        | bottom

    paren: "(" type ")"

    union: type "|" type -> union

    prim: "int" -> int
        | "integer" -> int
        | "float" -> float
        | "str" -> string
        | "string" -> string
        | "bool" -> bool
        | "boolean" -> bool

    bottom: "⊥" -> bottom
        | "bottom" -> bottom


    %import common.WS
    %ignore WS
"""
