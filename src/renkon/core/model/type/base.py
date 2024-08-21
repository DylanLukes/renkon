# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from collections.abc import Hashable
from functools import lru_cache
from typing import Any, ClassVar, Self, override, Literal, Union, Annotated, TypeGuard

from lark.exceptions import LarkError
from annotated_types import Predicate
from lark import Transformer
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic_core import core_schema as cs

from renkon.core.model.type.parser import parser


def is_type_str(s: str) -> TypeGuard[TypeStr]:
    try:
        Type.parse_string(s)
        return True
    except LarkError:
        return False


type TypeStr = Union[
    Literal["int", "float", "string", "bool", "equatable", "comparable", "numeric"],
    Annotated[str, Predicate(is_type_str)]
]


class Type(BaseModel, ABC, Hashable):
    class Config:
        frozen = True

    @abstractmethod
    def is_equal(self, other: Type) -> bool:
        """
        Two types are equal iff they are equal under canonicalization.
        """
        ...

    @abstractmethod
    def is_equivalent(self, other: Type) -> bool:
        """
        Two types are equivalent iff they are equal under normalization,
        i.e. they are witnessed by exactly the same set of values.
        """
        ...

    def is_subtype(self, other: Type) -> bool:
        """
        A type is a subtype of another type iff all values of the former are also values of the latter.
        """
        return other.is_supertype(self)

    def is_supertype(self, other: Type) -> bool:
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
    def normalize(self) -> Type:
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
    def parse_string(cls, s: str) -> Type:
        """
        Parse a string representation of the type.
        """

        try:
            tree = parser.parse(s)
            return TreeToTypeTransformer().transform(tree)
        except LarkError as e:
            msg = f"Error parsing type string: {s!r}"
            raise ValueError(msg) from e

    def is_numeric(self) -> bool:
        return self.is_subtype(Type.numeric())

    def is_equatable(self) -> bool:
        return self.is_subtype(Type.equatable())

    def is_comparable(self) -> bool:
        return self.is_subtype(Type.comparable())

    def __str__(self) -> str:
        return self.dump_string()

    def __repr__(self) -> str:
        return f"Type({self.dump_string()})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Type):
            return super().__eq__(other)
        return self.is_equal(other)

    def __or__(self, other: Type) -> UnionType:
        return UnionType(ts=frozenset({self, other})).canonicalize()

    @abstractmethod
    def __hash__(self) -> int:
        ...

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

    @staticmethod
    def bottom() -> BottomType:
        return BottomType()

    @staticmethod
    def int() -> IntType:
        return IntType()

    @staticmethod
    def float() -> FloatType:
        return FloatType()

    @staticmethod
    def str() -> StringType:
        return StringType()

    @staticmethod
    def bool() -> BoolType:
        return BoolType()

    @staticmethod
    def union(*types: Type) -> UnionType:
        return UnionType(ts=frozenset(types))

    @staticmethod
    def equatable() -> UnionType:
        return Type.union(Type.int(), Type.str(), Type.bool())

    @staticmethod
    def comparable() -> UnionType:
        return Type.union(Type.int(), Type.float(), Type.str())

    @staticmethod
    def numeric() -> UnionType:
        return Type.union(Type.int(), Type.float())


class BottomType(Type):
    def is_equal(self, other: Type) -> bool:
        return isinstance(other, BottomType)

    def is_equivalent(self, other: Type) -> bool:
        return self.is_equal(other)

    def is_subtype(self, other: Type) -> bool:  # noqa: ARG002
        return True

    def is_supertype(self, other: Type) -> bool:
        return self.is_equal(other)

    def canonicalize(self) -> Self:
        return self

    def normalize(self) -> Type:
        return self

    def dump_string(self) -> str:
        return "⊥"

    def __init__(self, /, **data: Any) -> None:
        if not data:
            return
        super().__init__(**data)

    def __hash__(self) -> int:
        return hash(BottomType)


# region Primitive Types


class PrimitiveType(Type):
    name: ClassVar[str]

    _all_subclasses: ClassVar[dict[str, type[PrimitiveType]]] = {}

    @override
    def is_equal(self, other: Type) -> bool:
        return type(other) == type(self)

    @override
    def is_equivalent(self, other: Type) -> bool:
        return self.is_equal(other)

    @override
    def is_subtype(self, other: Type) -> bool:
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


class UnionType(Type):
    ts: frozenset[Type]

    @property
    def is_empty_union(self) -> bool:
        return not self.ts

    @property
    def is_trivial_union(self) -> bool:
        """True if the union is of one unique type."""
        return len(self.ts) == 1

    @property
    def has_nested_union(self) -> bool:
        """True if the union contains an immediate child Union."""
        return any(isinstance(t, UnionType) for t in self.ts)

    @override
    def is_equal(self, other: Type) -> bool:
        return isinstance(other, UnionType) and self.ts == other.ts

    @override
    def is_equivalent(self, other: Type) -> bool:
        return self.normalize() == other.normalize()

    @override
    def is_subtype(self, other: Type) -> bool:
        if isinstance(other, UnionType):
            return self.canonicalize().ts.issubset(other.canonicalize().ts)
        return super().is_subtype(other)

    @override
    def is_supertype(self, other: Type) -> bool:
        return other in self.canonicalize().ts

    @override
    def canonicalize(self) -> UnionType:
        flat = self.flatten()
        if flat.is_trivial_union and isinstance(flat.single(), BottomType):
            return UnionType(ts=frozenset())
        return flat

    @override
    def normalize(self) -> Type:
        canon = self.canonicalize()

        if canon.is_empty_union:
            return BottomType()
        if canon.is_trivial_union:
            return canon.single()
        return canon

    def union(self, other: UnionType) -> UnionType:
        return UnionType(ts=self.ts.union(other.ts)).canonicalize()

    def intersect(self, other: UnionType) -> UnionType:
        return UnionType(ts=self.ts.intersection(other.ts)).canonicalize()

    def dump_string(self) -> str:
        if self.is_empty_union:
            return "⊥ | ⊥"
        if self.is_trivial_union:
            return f"{self.single().dump_string()} | ⊥"
        return " | ".join(sorted(t.dump_string() for t in self.ts))

    def flatten(self) -> UnionType:
        """Recursively flatten nested unions."""
        if not self.has_nested_union:
            return self
        ts: set[Type] = set()
        for t in self.ts:
            if isinstance(t, UnionType):
                ts.update(t.flatten().ts)
            else:
                ts.add(t)
        return UnionType.model_validate({"ts": ts})

    def single(self) -> Type:
        if not self.is_trivial_union:
            msg = "Union is not trivial, a single type"
            raise ValueError(msg)
        return next(iter(self.ts))

    def __hash__(self) -> int:
        return hash((type(self), self.ts))

    def __and__(self, other: UnionType) -> UnionType:
        return UnionType(ts=self.ts.intersection(other.ts)).canonicalize()


# endregion

# region


# noinspection PyMethodMayBeStatic
class TreeToTypeTransformer(Transformer[Type]):
    def type(self, type_: list[Type]):
        return type_[0]

    def int(self, _) -> IntType:
        return Type.int()

    def float(self, _) -> FloatType:
        return Type.float()

    def string(self, _) -> StringType:
        return Type.str()

    def bool(self, _) -> BoolType:
        return Type.bool()

    def bottom(self, _) -> BottomType:
        return Type.bottom()

    def union(self, types: list[Type]) -> UnionType:
        return Type.union(*types).canonicalize()

    def equatable(self, _) -> UnionType:
        return Type.equatable()

    def comparable(self, _) -> UnionType:
        return Type.comparable()

    def numeric(self, _) -> UnionType:
        return Type.numeric()

    def paren(self, type_: list[Type]) -> Type:
        return type_[0]

# endregion
