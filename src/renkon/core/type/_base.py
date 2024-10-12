# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Hashable
from typing import Any, ClassVar, Self, TypeGuard, override

from lark import Lark, Transformer
from lark.exceptions import LarkError
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic_core import core_schema as cs


class RenkonType(BaseModel, ABC, Hashable):
    class Config:
        frozen = True

    @abstractmethod
    def is_equal(self, other: RenkonType) -> bool:
        """
        Two types are equal iff they are equal under canonicalization.
        """
        ...

    @abstractmethod
    def is_equivalent(self, other: RenkonType) -> bool:
        """
        Two types are equivalent iff they are equal under normalization,
        i.e. they are witnessed by exactly the same set of values.
        """
        ...

    def is_subtype(self, other: RenkonType) -> bool:
        """
        A type is a subtype of another type iff all values of the former are also values of the latter.
        """
        return other.is_supertype(self)

    def is_supertype(self, other: RenkonType) -> bool:
        """
        A type is a supertype of another type iff the latter is a subtype of the former.
        """
        return other.is_subtype(self)

    @abstractmethod
    def canonicalize(self) -> Self:
        """
        Return a canonical representation of the type.
        """
        ...

    @abstractmethod
    def normalize(self) -> RenkonType:
        """
        Return a normalized representation of the type, which may be of a different, simpler type.
        """
        ...

    @abstractmethod
    def dump_string(self) -> str:
        """
        Dump a string representation of the type.
        """
        ...

    @classmethod
    def parse_string(cls, s: str) -> RenkonType:
        """
        Parse a string representation of the type.
        """

        try:
            # This parser has a transformer, so does not return Tree.
            return parser.parse(s)  # type: ignore
        except LarkError as e:
            msg = f"Error parsing type string: {s!r}"
            raise ValueError(msg) from e

    @classmethod
    def numeric_types(cls) -> frozenset[RenkonType]:
        return frozenset({Int(), Float()})

    @classmethod
    def equatable_types(cls) -> frozenset[RenkonType]:
        return frozenset({Int(), String(), Bool()})

    @classmethod
    def comparable_types(cls) -> frozenset[RenkonType]:
        return frozenset({Int(), Float(), String()})

    def is_concrete(self) -> bool:
        return isinstance(self, Primitive)

    def is_union_of_concrete(self) -> TypeGuard[Union]:
        return self.is_union() and all(ty.is_concrete() for ty in self.ts)

    def is_abstract(self) -> bool:
        return not self.is_concrete()

    def is_int(self) -> TypeGuard[Int]:
        return type(self) is Int

    def is_float(self) -> TypeGuard[Float]:
        return type(self) is Float

    def is_str(self) -> TypeGuard[String]:
        return type(self) is String

    def is_bool(self) -> TypeGuard[Bool]:
        return type(self) is Bool

    def is_union(self) -> TypeGuard[Union]:
        return isinstance(self, Union)

    def is_numeric(self) -> bool:
        return self.is_subtype(Union(ts=self.numeric_types()))

    def is_equatable(self) -> bool:
        return self.is_subtype(Union(ts=self.equatable_types()))

    def is_comparable(self) -> bool:
        return self.is_subtype(Union(ts=self.comparable_types()))

    def __str__(self) -> str:
        return self.dump_string()

    def __repr__(self) -> str:
        return f"Type({self.dump_string()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RenkonType):
            return super().__eq__(other)
        return self.is_equal(other)

    def __and__(self, other: RenkonType) -> RenkonType:
        return Union(self).intersect(Union(other)).normalize()

    def __or__(self, other: RenkonType) -> Union:
        return Union(self).union(Union(other)).canonicalize()

    @abstractmethod
    def __hash__(self) -> int: ...

    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[BaseModel], handler: GetCoreSchemaHandler, /) -> CoreSchema:
        schema = cls.__dict__.get("__pydantic_core_schema__")
        if schema is not None:
            return schema

        string_schema = cs.chain_schema([cs.str_schema(), cs.no_info_plain_validator_function(cls.parse_string)])
        serializer = cs.plain_serializer_function_ser_schema(lambda t: t.dump_string())

        return cs.json_or_python_schema(
            python_schema=cs.union_schema([string_schema, handler(cls)]),
            json_schema=string_schema,
            serialization=serializer,
        )


class Top(RenkonType):
    def __init__(self, /, **data: Any) -> None:
        if not data:
            return
        super().__init__(**data)

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return isinstance(other, Top)

    @override
    def is_equivalent(self, other: RenkonType) -> bool:
        return self.is_equal(other)

    @override
    def is_subtype(self, other: RenkonType) -> bool:
        return False

    @override
    def is_supertype(self, other: RenkonType) -> bool:
        return self.is_equal(other)

    @override
    def canonicalize(self) -> Self:
        return self

    @override
    def normalize(self) -> RenkonType:
        return self

    @override
    def dump_string(self) -> str:
        return "any"

    @override
    def __hash__(self) -> int:
        return hash(Top)


class Bottom(RenkonType):
    def __init__(self, /, **data: Any) -> None:
        if not data:
            return
        super().__init__(**data)

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return isinstance(other, Bottom)

    @override
    def is_equivalent(self, other: RenkonType) -> bool:
        return self.is_equal(other)

    @override
    def is_subtype(self, other: RenkonType) -> bool:
        return True

    @override
    def is_supertype(self, other: RenkonType) -> bool:
        return self.is_equal(other)

    @override
    def canonicalize(self) -> Self:
        return self

    @override
    def normalize(self) -> RenkonType:
        return self

    @override
    def dump_string(self) -> str:
        return "none"

    @override
    def __hash__(self) -> int:
        return hash(Bottom)


class Primitive(RenkonType):
    name: ClassVar[str]

    _all_subclasses: ClassVar[dict[str, type[Primitive]]] = {}

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return type(other) is type(self)

    @override
    def is_equivalent(self, other: RenkonType) -> bool:
        return self.is_equal(other)

    @override
    def is_subtype(self, other: RenkonType) -> bool:
        if isinstance(other, Primitive):
            return self.name == other.name
        return super().is_subtype(other)

    @override
    def canonicalize(self) -> Primitive:
        return self

    @override
    def normalize(self) -> Primitive:
        return self

    @override
    def dump_string(self) -> str:
        return self.name

    def __init__(self, /, **data: Any) -> None:
        if not data:
            return
        super().__init__(**data)

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, name: str, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        cls.name = name
        Primitive._all_subclasses[name] = cls

    def __hash__(self) -> int:
        return hash(self.name)


class Int(Primitive, name="int"):
    def is_subtype(self, other: RenkonType) -> bool:
        return type(other) is Float or super().is_subtype(other)


class Float(Primitive, name="float"): ...


class String(Primitive, name="string"): ...


class Bool(Primitive, name="bool"): ...


class Union(RenkonType):
    ts: frozenset[RenkonType]

    def __init__(self, /, *ts: RenkonType, **data: Any) -> None:
        if ts and data:
            msg = "UnionType may be initialized either from a list of types or from keyword arguments, not both."
            raise ValueError(msg)

        if not ts and not data:
            data["ts"] = frozenset()
        elif ts:
            data["ts"] = frozenset(ts)

        super().__init__(**data)

    def is_empty_union(self) -> bool:
        return not self.ts

    def is_trivial_union(self) -> bool:
        """True if the union is of one unique type."""
        return len(self.ts) == 1

    def contains_top(self) -> bool:
        """True if the union contains (at any depth) a TopType."""
        return bool(any(isinstance(t, Top) for t in self.flatten().ts))

    def contains_bottom(self) -> bool:
        """True if the union contains (at any depth) a BottomType."""
        return bool(any(isinstance(t, Bottom) for t in self.flatten().ts))

    def contains_union(self) -> bool:
        """True if the union contains an immediate child Union."""
        return bool(any(isinstance(t, Union) for t in self.ts))

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return isinstance(other, Union) and self.ts == other.ts

    @override
    def is_equivalent(self, other: RenkonType) -> bool:
        return self.normalize() == other.normalize()

    @override
    def is_subtype(self, other: RenkonType) -> bool:
        if isinstance(other, Union):
            return self.canonicalize().ts.issubset(other.canonicalize().ts)
        return super().is_subtype(other)

    @override
    def is_supertype(self, other: RenkonType) -> bool:
        return other in self.canonicalize().ts

    @override
    def canonicalize(self) -> Union:
        flat = self.flatten()
        ts = flat.ts

        # If a top type is present, leave only it.
        if self.contains_top():
            return Union(ts=frozenset({Top()}))

        # Remove any bottom types.
        ts = filter(lambda t: not isinstance(t, Bottom), ts)
        return Union(ts=frozenset(ts))

    @override
    def normalize(self) -> RenkonType:
        canon = self.canonicalize()

        if canon.contains_top():
            return Top()
        if canon.is_empty_union():
            return Bottom()
        if canon.is_trivial_union():
            return canon.single()
        return canon

    def union(self, other: Union) -> Union:
        return Union(ts=self.ts.union(other.canonicalize().ts)).canonicalize()

    def intersect(self, other: Union) -> Union:
        if self.contains_top():
            return other.canonicalize()
        if other.contains_top():
            return self.canonicalize()

        return Union(ts=self.ts.intersection(other.canonicalize().ts)).canonicalize()

    def dump_string(self) -> str:
        if self.is_empty_union():
            return "none | none"
        if self.is_trivial_union():
            return f"{self.single().dump_string()} | none"
        return " | ".join(sorted(t.dump_string() for t in self.ts))

    def flatten(self) -> Union:
        """Recursively flatten nested unions."""
        if not self.contains_union():
            return self
        ts: set[RenkonType] = set()
        for t in self.ts:
            if isinstance(t, Union):
                ts.update(t.flatten().ts)
            else:
                ts.add(t)
        return Union.model_validate({"ts": ts})

    def single(self) -> RenkonType:
        if not self.is_trivial_union():
            msg = "Union is not trivial, a single type"
            raise ValueError(msg)
        return next(iter(self.ts))

    def __hash__(self) -> int:
        return hash((type(self), self.ts))


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
"""  # noqa: RUF001


# noinspection PyMethodMayBeStatic
class RenkonTypeTreeTransformer(Transformer[RenkonType]):
    @staticmethod
    def type(type_: list[RenkonType]):
        return type_[0]

    @staticmethod
    def int(_) -> Int:
        return Int()

    @staticmethod
    def float(_) -> Float:
        return Float()

    @staticmethod
    def string(_) -> String:
        return String()

    @staticmethod
    def bool(_) -> Bool:
        return Bool()

    @staticmethod
    def top(_) -> RenkonType:
        return Top()

    @staticmethod
    def bottom(_) -> Bottom:
        return Bottom()

    @staticmethod
    def union(types: list[RenkonType]) -> Union:
        return Union(ts=frozenset(types)).canonicalize()

    @staticmethod
    def numeric(_) -> Union:
        return Union(ts=frozenset(RenkonType.numeric_types()))

    @staticmethod
    def equatable(_) -> Union:
        return Union(ts=frozenset(RenkonType.equatable_types()))

    @staticmethod
    def comparable(_) -> Union:
        return Union(ts=frozenset(RenkonType.comparable_types()))

    @staticmethod
    def paren(type_: list[RenkonType]) -> RenkonType:
        return type_[0]


transformer = RenkonTypeTreeTransformer()
parser = Lark(grammar, lexer="standard", parser="lalr", transformer=transformer)
