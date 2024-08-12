# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Hashable
from typing import Any, ClassVar, Self, override

from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic_core import core_schema as cs


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
    @abstractmethod
    def validate_string(cls, s: str) -> Self:
        """
        Parse a string representation of the type.
        """
        ...

    def is_numeric(self) -> bool:
        return self.is_subtype(rk_numeric)

    def is_equatable(self) -> bool:
        return self.is_subtype(rk_equatable)

    def is_comparable(self) -> bool:
        return self.is_subtype(rk_comparable)

    def __str__(self) -> str:
        return self.dump_string()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Type):
            return super().__eq__(other)
        return self.is_equal(other)

    def __or__(self, other: Type) -> Union:
        return Union(ts=frozenset({self, other})).canonicalize()

    @abstractmethod
    def __hash__(self) -> int:
        ...

    @classmethod
    def __get_pydantic_core_schema__(cls, source: type[BaseModel], handler: GetCoreSchemaHandler, /) -> CoreSchema:
        string_schema = cs.chain_schema([
            cs.str_schema(),
            cs.no_info_plain_validator_function(cls.validate_string)
        ])
        serializer = cs.plain_serializer_function_ser_schema(lambda t: t.dump_string())

        return cs.json_or_python_schema(
            python_schema=cs.union_schema([string_schema, handler(cls)]),
            json_schema=cs.json_schema(schema=string_schema),
            serialization=serializer
        )


class Bottom(Type):
    def is_equal(self, other: Type) -> bool:
        return isinstance(other, Bottom)

    def is_equivalent(self, other: Type) -> bool:
        return self.is_equal(other)

    def is_subtype(self, other: Type) -> bool:
        return True

    def is_supertype(self, other: Type) -> bool:
        return self.is_equal(other)

    def canonicalize(self) -> Self:
        return self

    def normalize(self) -> Type:
        return self

    def dump_string(self) -> str:
        return "⊥"

    @classmethod
    def validate_string(cls, s: str) -> Self:
        if s == "⊥":
            return cls()
        msg = f"Invalid bottom type string: {s}"
        raise ValueError(msg)

    def __hash__(self) -> int:
        return hash(Bottom)


# region Primitive Types

class Primitive(Type):
    name: ClassVar[str]

    _all_subclasses: ClassVar[dict[str, type[Primitive]]] = {}

    @override
    def is_equal(self, other: Type) -> bool:
        return type(other) == type(self)

    @override
    def is_equivalent(self, other: Type) -> bool:
        return self.is_equal(other)

    @override
    def is_subtype(self, other: Type) -> bool:
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

    @classmethod
    def validate_string(cls, s: str) -> Primitive:
        return Primitive._all_subclasses[s]()

    def __init__(self, /, **data: Any) -> None:
        if not data:
            return
        super().__init__(**data)

    def __init_subclass__(cls, name: str, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        cls.name = name
        Primitive._all_subclasses[name] = cls

    def __hash__(self) -> int:
        return hash(self.name)


class Int(Primitive, name="int"): ...


class Float(Primitive, name="float"): ...


class String(Primitive, name="string"): ...


class Bool(Primitive, name="bool"): ...


# endregion

# region Union Type

class Union(Type):
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
        return any(isinstance(t, Union) for t in self.ts)

    @override
    def is_equal(self, other: Type) -> bool:
        return isinstance(other, Union) and self.ts == other.ts

    @override
    def is_equivalent(self, other: Type) -> bool:
        return self.normalize() == other.normalize()

    @override
    def is_subtype(self, other: Type) -> bool:
        if isinstance(other, Union):
            return self.canonicalize().ts.issubset(other.canonicalize().ts)
        return super().is_subtype(other)

    @override
    def is_supertype(self, other: Type) -> bool:
        return other in self.canonicalize().ts

    @override
    def canonicalize(self) -> Union:
        return self.flatten()

    @override
    def normalize(self) -> Type:
        canon = self.canonicalize()

        if canon.is_empty_union:
            return Bottom()
        elif canon.is_trivial_union:
            return next(iter(canon.ts))
        return canon

    def union(self, other: Union) -> Union:
        return Union(ts=self.ts.union(other.ts)).canonicalize()

    def intersect(self, other: Union) -> Union:
        return Union(ts=self.ts.intersection(other.ts)).canonicalize()

    def dump_string(self) -> str:
        if self.is_empty_union:
            return "⊥ | ⊥"
        elif self.is_trivial_union:
            return f"{next(iter(self.ts)).dump_string()} | ⊥"
        return " | ".join(sorted(t.dump_string() for t in self.ts))

    @classmethod
    def validate_string(cls, s: str) -> Union:
        raise NotImplementedError

    def flatten(self) -> Union:
        """Recursively flatten nested unions."""
        if not self.has_nested_union:
            return self
        ts: set[Type] = set()
        for t in self.ts:
            if isinstance(t, Union):
                ts.update(t.flatten().ts)
            else:
                ts.add(t)
        return Union.model_validate({'ts': ts})

    def __hash__(self) -> int:
        return hash((type(self), self.ts))

    def __and__(self, other: Union) -> Union:
        return Union(ts=self.ts.intersection(other.ts)).canonicalize()


# endregion

# region

rk_bottom = Bottom()

rk_int = Int()
rk_float = Float()
rk_str = String()
rk_bool = Bool()


def rk_union(*ts: Type) -> Union:
    return Union.model_validate({'ts': ts})


rk_numeric = rk_int | rk_float
rk_equatable = rk_int | rk_str | rk_bool
rk_comparable = rk_int | rk_float | rk_str

# endregion


# region
