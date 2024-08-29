# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Hashable
from typing import Annotated, Any, ClassVar, Literal, Self, TypeGuard, override

from annotated_types import Predicate
from lark import Transformer
from lark.exceptions import LarkError
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic_core import core_schema as cs

from renkon.core.model.type.parser import parser


def is_type_str(s: str) -> TypeGuard[TypeStr]:
    try:
        RenkonType.parse_string(s)
    except LarkError:
        return False
    else:
        return True


type TypeStr = (
    Literal["int", "float", "string", "bool", "equatable", "comparable", "numeric"]
    | Annotated[str, Predicate(is_type_str)]
)


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
            tree = parser.parse(s)
            return TreeToTypeTransformer().transform(tree)
        except LarkError as e:
            msg = f"Error parsing type string: {s!r}"
            raise ValueError(msg) from e

    @classmethod
    def numeric_types(cls) -> frozenset[RenkonType]:
        return frozenset({IntType(), FloatType()})

    @classmethod
    def equatable_types(cls) -> frozenset[RenkonType]:
        return frozenset({IntType(), StringType(), BoolType()})

    @classmethod
    def comparable_types(cls) -> frozenset[RenkonType]:
        return frozenset({IntType(), FloatType(), StringType()})

    def is_numeric(self) -> bool:
        return self.is_subtype(UnionType(ts=self.numeric_types()))

    def is_equatable(self) -> bool:
        return self.is_subtype(UnionType(ts=self.equatable_types()))

    def is_comparable(self) -> bool:
        return self.is_subtype(UnionType(ts=self.comparable_types()))

    def __str__(self) -> str:
        return self.dump_string()

    def __repr__(self) -> str:
        return f"Type({self.dump_string()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RenkonType):
            return super().__eq__(other)
        return self.is_equal(other)

    def __and__(self, other: RenkonType) -> RenkonType:
        return UnionType(self).intersect(UnionType(other)).normalize()

    def __or__(self, other: RenkonType) -> UnionType:
        return UnionType(self).union(UnionType(other)).canonicalize()

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


class TopType(RenkonType):
    def __init__(self, /, **data: Any) -> None:
        if not data:
            return
        super().__init__(**data)

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return isinstance(other, TopType)

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
        return hash(TopType)


class BottomType(RenkonType):
    def __init__(self, /, **data: Any) -> None:
        if not data:
            return
        super().__init__(**data)

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return isinstance(other, BottomType)

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
        return hash(BottomType)


# region Primitive Types


class PrimitiveType(RenkonType):
    name: ClassVar[str]

    _all_subclasses: ClassVar[dict[str, type[PrimitiveType]]] = {}

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return type(other) is type(self)

    @override
    def is_equivalent(self, other: RenkonType) -> bool:
        return self.is_equal(other)

    @override
    def is_subtype(self, other: RenkonType) -> bool:
        if isinstance(other, PrimitiveType):
            return self.name == other.name
        return super().is_subtype(other)

    @override
    def canonicalize(self) -> PrimitiveType:
        return self

    @override
    def normalize(self) -> PrimitiveType:
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
        PrimitiveType._all_subclasses[name] = cls

    def __hash__(self) -> int:
        return hash(self.name)


class IntType(PrimitiveType, name="int"): ...


class FloatType(PrimitiveType, name="float"): ...


class StringType(PrimitiveType, name="string"): ...


class BoolType(PrimitiveType, name="bool"): ...


# endregion

# region Union Type


class UnionType(RenkonType):
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
        return bool(any(isinstance(t, TopType) for t in self.flatten().ts))

    def contains_bottom(self) -> bool:
        """True if the union contains (at any depth) a BottomType."""
        return bool(any(isinstance(t, BottomType) for t in self.flatten().ts))

    def contains_union(self) -> bool:
        """True if the union contains an immediate child Union."""
        return bool(any(isinstance(t, UnionType) for t in self.ts))

    @override
    def is_equal(self, other: RenkonType) -> bool:
        return isinstance(other, UnionType) and self.ts == other.ts

    @override
    def is_equivalent(self, other: RenkonType) -> bool:
        return self.normalize() == other.normalize()

    @override
    def is_subtype(self, other: RenkonType) -> bool:
        if isinstance(other, UnionType):
            return self.canonicalize().ts.issubset(other.canonicalize().ts)
        return super().is_subtype(other)

    @override
    def is_supertype(self, other: RenkonType) -> bool:
        return other in self.canonicalize().ts

    @override
    def canonicalize(self) -> UnionType:
        flat = self.flatten()
        ts = flat.ts

        # If a top type is present, leave only it.
        if self.contains_top():
            return UnionType(ts=frozenset({TopType()}))

        # Remove any bottom types.
        ts = filter(lambda t: not isinstance(t, BottomType), ts)
        return UnionType(ts=frozenset(ts))

    @override
    def normalize(self) -> RenkonType:
        canon = self.canonicalize()

        if canon.contains_top():
            return TopType()
        if canon.is_empty_union():
            return BottomType()
        if canon.is_trivial_union():
            return canon.single()
        return canon

    def union(self, other: UnionType) -> UnionType:
        return UnionType(ts=self.ts.union(other.canonicalize().ts)).canonicalize()

    def intersect(self, other: UnionType) -> UnionType:
        if self.contains_top():
            return other.canonicalize()
        if other.contains_top():
            return self.canonicalize()

        return UnionType(ts=self.ts.intersection(other.canonicalize().ts)).canonicalize()

    def dump_string(self) -> str:
        if self.is_empty_union():
            return "none | none"
        if self.is_trivial_union():
            return f"{self.single().dump_string()} | none"
        return " | ".join(sorted(t.dump_string() for t in self.ts))

    def flatten(self) -> UnionType:
        """Recursively flatten nested unions."""
        if not self.contains_union():
            return self
        ts: set[RenkonType] = set()
        for t in self.ts:
            if isinstance(t, UnionType):
                ts.update(t.flatten().ts)
            else:
                ts.add(t)
        return UnionType.model_validate({"ts": ts})

    def single(self) -> RenkonType:
        if not self.is_trivial_union():
            msg = "Union is not trivial, a single type"
            raise ValueError(msg)
        return next(iter(self.ts))

    def __hash__(self) -> int:
        return hash((type(self), self.ts))


# endregion

# region


# noinspection PyMethodMayBeStatic
class TreeToTypeTransformer(Transformer[RenkonType]):
    @staticmethod
    def type(type_: list[RenkonType]):
        return type_[0]

    @staticmethod
    def int(_) -> IntType:
        return IntType()

    @staticmethod
    def float(_) -> FloatType:
        return FloatType()

    @staticmethod
    def string(_) -> StringType:
        return StringType()

    @staticmethod
    def bool(_) -> BoolType:
        return BoolType()

    @staticmethod
    def top(_) -> RenkonType:
        return TopType()

    @staticmethod
    def bottom(_) -> BottomType:
        return BottomType()

    @staticmethod
    def union(types: list[RenkonType]) -> UnionType:
        return UnionType(ts=frozenset(types)).canonicalize()

    @staticmethod
    def numeric(_) -> UnionType:
        return UnionType(ts=frozenset(RenkonType.numeric_types()))

    @staticmethod
    def equatable(_) -> UnionType:
        return UnionType(ts=frozenset(RenkonType.equatable_types()))

    @staticmethod
    def comparable(_) -> UnionType:
        return UnionType(ts=frozenset(RenkonType.comparable_types()))

    @staticmethod
    def paren(type_: list[RenkonType]) -> RenkonType:
        return type_[0]


# endregion
