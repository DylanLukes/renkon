# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Hashable, Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self, cast, final, overload, override

from lark import Lark, Transformer
from lark.exceptions import LarkError
from pydantic_core import core_schema as cs

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler

type RenkonTypeLiteralStr = Literal["int", "float", "bool", "str", "comparable", "equatable", "numeric"]


class RenkonType(ABC):
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
    def dumps(self) -> str:
        """
        Dump a string representation of the type.
        """
        ...

    @classmethod
    def loads(cls, s: str) -> RenkonType:
        """
        Parse a string representation of the type.
        """

        try:
            # This parser has a transformer, so does not return Tree.
            return parser.parse(s)  # type: ignore
        except LarkError as e:
            msg = f"Error parsing type string: {s!r}"
            raise ValueError(msg) from e

    def __str__(self) -> str:
        return self.dumps()

    def __repr__(self) -> str:
        return f"Type({self.dumps()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RenkonType):
            return super().__eq__(other)
        return self.is_equal(other)

    def __hash__(self) -> int: ...

    def __and__(self, other: RenkonType) -> RenkonType:
        return Union(self).intersect(Union(other)).normalize()

    def __or__(self, other: RenkonType) -> Union:
        return Union(self).union(Union(other)).canonicalize()

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, handler: GetCoreSchemaHandler, /) -> cs.CoreSchema:
        from_str_schema = cs.chain_schema([
            cs.str_schema(),
            cs.no_info_plain_validator_function(cls.loads),
        ])

        return cs.json_or_python_schema(
            python_schema=cs.union_schema([from_str_schema, cs.is_instance_schema(cls)]),
            json_schema=from_str_schema,
            serialization=cs.plain_serializer_function_ser_schema(lambda t: t.dumps()),
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
    def dumps(self) -> str:
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
    def dumps(self) -> str:
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
    def dumps(self) -> str:
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

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)


@final
class Int(Primitive, Hashable, name="int"):
    def is_subtype(self, other: RenkonType) -> bool:
        return type(other) is Float or super().is_subtype(other)


@final
class Float(Primitive, Hashable, name="float"): ...


@final
class String(Primitive, Hashable, name="string"): ...


@final
class Bool(Primitive, Hashable, name="bool"): ...


class Union(RenkonType):
    members: frozenset[RenkonType]

    @overload
    def __init__(self, members: Iterable[RenkonType], /) -> None: ...

    @overload
    def __init__(self, *members: RenkonType) -> None: ...

    def __init__(self, *members: RenkonType | Iterable[RenkonType]) -> None:
        if len(members) == 1 and isinstance(members[0], Iterable):
            self.members = frozenset(members[0])
        else:
            self.members = frozenset(cast(Iterable[RenkonType], members))

    def is_empty_union(self) -> bool:
        return not self.members

    def is_trivial_union(self) -> bool:
        """True if the union is of one unique type."""
        return len(self.members) == 1

    def contains_top(self) -> bool:
        """True if the union contains (at any depth) a TopType."""
        return bool(any(isinstance(t, Top) for t in self.flatten().members))

    def contains_bottom(self) -> bool:
        """True if the union contains (at any depth) a BottomType."""
        return bool(any(isinstance(t, Bottom) for t in self.flatten().members))

    def contains_union(self) -> bool:
        """True if the union contains an immediate child Union."""
        return bool(any(isinstance(t, Union) for t in self.members))

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return isinstance(other, Union) and self.members == other.members

    @override
    def is_equivalent(self, other: RenkonType) -> bool:
        return self.normalize() == other.normalize()

    @override
    def is_subtype(self, other: RenkonType) -> bool:
        if isinstance(other, Union):
            return self.canonicalize().members.issubset(other.canonicalize().members)
        return super().is_subtype(other)

    @override
    def is_supertype(self, other: RenkonType) -> bool:
        return other in self.canonicalize().members

    @override
    def canonicalize(self) -> Union:
        # If a top type is present, leave only it.
        if self.contains_top():
            return Union(Top())

        return Union(filter(lambda t: not isinstance(t, Bottom), self.flatten().members))

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
        return Union(self.members.union(other.canonicalize().members)).canonicalize()

    def intersect(self, other: Union) -> Union:
        if self.contains_top():
            return other.canonicalize()
        if other.contains_top():
            return self.canonicalize()

        return Union(self.members.intersection(other.canonicalize().members)).canonicalize()

    def dumps(self) -> str:
        if self.is_empty_union():
            return "none | none"
        if self.is_trivial_union():
            return f"{self.single().dumps()} | none"
        return " | ".join(sorted(t.dumps() for t in self.members))

    def flatten(self) -> Union:
        """Recursively flatten nested unions."""
        if not self.contains_union():
            return self
        members: set[RenkonType] = set()
        for member in self.members:
            if isinstance(member, Union):
                members.update(member.flatten().members)
            else:
                members.add(member)
        return Union(members)

    def single(self) -> RenkonType:
        if not self.is_trivial_union():
            msg = "Union is not trivial, a single type"
            raise ValueError(msg)
        return next(iter(self.members))

    def __hash__(self) -> int:
        return hash((type(self), self.members))


NUMERIC_TYPES = frozenset({Int(), Float()})
EQUATABLE_TYPES = frozenset({Int(), String(), Bool()})
COMPARABLE_TYPES = frozenset({Int(), Float(), String()})


class Numeric(Union):
    def __init__(self, /):
        super().__init__(*NUMERIC_TYPES)


class Equatable(Union):
    def __init__(self, /):
        super().__init__(*EQUATABLE_TYPES)


class Comparable(Union):
    def __init__(self, /):
        super().__init__(*COMPARABLE_TYPES)


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
        return Union(types).canonicalize()

    @staticmethod
    def numeric(_) -> Union:
        return Numeric()

    @staticmethod
    def equatable(_) -> Union:
        return Equatable()

    @staticmethod
    def comparable(_) -> Union:
        return Comparable()

    @staticmethod
    def paren(type_: list[RenkonType]) -> RenkonType:
        return type_[0]


transformer = RenkonTypeTreeTransformer()
parser = Lark(grammar, lexer="standard", parser="lalr", transformer=transformer)
