grammar = r"""
    ?start: type

    type: paren
        | union
        | primitive
        | special
        | bottom

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

    bottom: "⊥" -> bottom
        | "bottom" -> bottom


    %import common.WS
    %ignore WS
"""
