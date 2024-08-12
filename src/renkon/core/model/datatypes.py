# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar, Protocol, Self, final, runtime_checkable

import polars as pl
import pytest
from polars import PolarsDataType
from pydantic import GetCoreSchemaHandler, TypeAdapter
from pydantic_core import CoreSchema
from pydantic_core import core_schema as cs

from renkon.util.singleton import Singleton, singletonmethod

if TYPE_CHECKING:
    from polars.type_aliases import PythonDataType


class TypeSystem(Singleton):
    """
    Represents the entire Renkon data type system. This is a singleton rather than module-level
    state to allow for easy extension and testing of the data type system in the future.
    """

    _code_to_type: dict[str, RenkonType] = {}
    _type_to_code: dict[RenkonType, str] = {}

    _rk_to_pl: dict[RenkonType, PolarsDataType] = {}
    _pl_to_rk: dict[PolarsDataType, RenkonType] = {}

    _rk_to_py: dict[RenkonType, PythonDataType] = {}
    _py_to_rk: dict[PythonDataType, RenkonType] = {}

    @singletonmethod
    def int_type(self) -> IntType:
        return IntType()

    @singletonmethod
    def float_type(self) -> FloatType:
        return FloatType()

    @singletonmethod
    def string_type(self) -> StringType:
        return StringType()

    @singletonmethod
    def boolean_type(self) -> BooleanType:
        return BooleanType()

    @singletonmethod
    def register_primitive_type(self, renkon_type: PrimitiveType) -> None:
        def register_helper[K, V](d: dict[K, V], key: K, value: V, key_name: str, value_name: str) -> None:
            if key in d:
                msg = f"{key_name} '{key}' is already registered to {value_name} '{d[key]}'"
                raise KeyError(msg)
            d[key] = value

        register_helper(self._code_to_type, renkon_type.code, renkon_type, "string code", "Renkon type")
        register_helper(self._type_to_code, renkon_type, renkon_type.code, "Renkon type", "string code")

        register_helper(self._rk_to_pl, renkon_type, renkon_type.to_polars, "Renkon type", "Polars type")
        for polars_type in renkon_type.from_polars:
            register_helper(self._pl_to_rk, polars_type, renkon_type, "Polars type", "Renkon type")

        register_helper(self._rk_to_py, renkon_type, renkon_type.to_python, "Renkon type", "Python type")
        for pyty in renkon_type.from_python:
            register_helper(self._py_to_rk, pyty, renkon_type, "Python type", "Renkon type")

    @singletonmethod
    def get_all_convertible_polars_types(self) -> Iterable[PolarsDataType]:
        return self._pl_to_rk.keys()

    @singletonmethod
    def get_all_convertible_python_types(self) -> Iterable[PythonDataType]:
        return self._py_to_rk.keys()

    @singletonmethod
    def from_code(self, code: str) -> RenkonType | None:
        return self._code_to_type.get(code)

    @singletonmethod
    def to_code(self, renkon_type: RenkonType) -> str | None:
        return self._type_to_code.get(renkon_type)

    @singletonmethod
    def from_polars(self, polars_type: PolarsDataType) -> RenkonType | None:
        return self._pl_to_rk.get(polars_type)

    @singletonmethod
    def to_polars(self, renkon_type: RenkonType) -> PolarsDataType | None:
        return self._rk_to_pl.get(renkon_type)

    @singletonmethod
    def from_python(self, pyty: PythonDataType) -> RenkonType | None:
        return self._py_to_rk.get(pyty)

    @singletonmethod
    def to_python(self, renkon_type: RenkonType) -> PythonDataType | None:
        return self._rk_to_py.get(renkon_type)


@runtime_checkable
class RenkonType(Protocol):
    @property
    @abstractmethod
    def code(self) -> str:
        ...

    def is_same_type(self, other: RenkonType) -> bool:
        """Exact equality check."""
        return type(self) is type(other)

    @abstractmethod
    def is_strict_subtype(self, other: RenkonType) -> bool:
        """Strict subtype: All values of the other type are also values of this type, but they are not the same type."""
        ...

    def is_strict_supertype(self, other: RenkonType) -> bool:
        return other.is_strict_subtype(self)

    def is_subtype(self, other: RenkonType) -> bool:
        return self.is_same_type(other) or self.is_strict_subtype(other)

    def is_supertype(self, other: RenkonType) -> bool:
        return self.is_same_type(other) or self.is_strict_supertype(other)

    def union[T: RenkonType](self, other: T) -> UnionType[Self, T]:
        return UnionType(self, other)

    def nullable(self) -> NullableType[Self]:
        return NullableType(self)

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.is_same_type(other)

    def __gt__(self, other: RenkonType) -> bool:
        return self.is_strict_supertype(other)

    def __lt__(self, other: RenkonType) -> bool:
        return self.is_strict_subtype(other)

    def __ge__(self, other: RenkonType) -> bool:
        return self.is_supertype(other)

    def __le__(self, other: RenkonType) -> bool:
        return self.is_subtype(other)

    def __or__[T: RenkonType](self, other: T) -> UnionType[Self, T]:
        return self.union(other)

    def __str__(self):
        return self.code

    def __repr__(self):
        return self.code

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # fmt: off
        def validate_from_code(code: str) -> RenkonType:
            renkon_type = TypeSystem.from_code(code)
            if renkon_type is None:
                msg = f"Renkon data type '{code}' is not recognized."
                raise ValueError(msg)
            return renkon_type

        def validate_from_polars(polars_type: PolarsDataType) -> RenkonType:
            renkon_type = TypeSystem.from_polars(polars_type)
            if renkon_type is None:
                msg = f"Polars data type '{polars_type}' is not convertible to a Renkon type."
                raise ValueError(msg)
            return renkon_type

        def validate_from_python(pyty: PythonDataType) -> RenkonType:
            renkon_type = TypeSystem.from_python(pyty)
            if renkon_type is None:
                msg = f"Python data type '{pyty}' is not convertible to a Renkon type."
                raise ValueError(msg)
            return renkon_type

        from_code_schema = cs.chain_schema([
            cs.str_schema(),
            cs.no_info_plain_validator_function(validate_from_code),
        ])

        from_polars_type_schema = cs.chain_schema([
            cs.is_subclass_schema(pl.DataType),
            # cs.union_schema([cs.is_instance_schema(polars_type)
            #                  for polars_type in TypeSystem.get_all_convertible_polars_types()]),
            cs.no_info_plain_validator_function(validate_from_polars),
        ])

        from_python_type_schema = cs.chain_schema([
            cs.is_subclass_schema(type),
            # cs.union_schema([cs.is_instance_schema(pyty)
            #                  for pyty in TypeSystem.get_all_convertible_python_types()]),
            cs.no_info_plain_validator_function(validate_from_python),
        ])

        return cs.json_or_python_schema(
            json_schema=from_code_schema,
            python_schema=cs.union_schema(
                [
                    cs.is_instance_schema(cls),
                    from_code_schema,
                    from_polars_type_schema,
                    from_python_type_schema
                ]
            ),
            serialization=cs.plain_serializer_function_ser_schema(str)
        )
        # fmt: on


class PrimitiveType(RenkonType, Protocol):
    from_polars: ClassVar[Iterable[PolarsDataType]]
    to_polars: ClassVar[PolarsDataType]
    from_python: ClassVar[Iterable[PythonDataType]]
    to_python: ClassVar[PythonDataType]

    def __init_subclass__(cls, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        TypeSystem.register_primitive_type(cls())

    def is_strict_subtype(self, other: RenkonType) -> bool:
        return other > self  # delegate to the other type

    def __hash__(self):
        return hash(type(self))


@final
class UnionType[T1: RenkonType, T2: RenkonType](RenkonType):
    """The least upper bound of T1 and T2."""
    t1: T1
    t2: T2

    def __init__(self, t1: T1, t2: T2):
        super().__init__()
        self.t1 = t1
        self.t2 = t2

    def is_same_type(self, other: Any) -> bool:
        if type(self) is type(other):
            return self.t1 == other.t1 and self.t2 == other.t2 \
                or self.t1 == other.t2 and self.t2 == other.t1
        return False

    def is_strict_subtype(self, other: RenkonType) -> bool:
        return False

    def is_strict_supertype(self, other: RenkonType) -> bool:
        """ (A | B) > A and (A | B) > B. """
        return self.t1 > other or self.t2 > other

    @property
    def code(self) -> str:
        return f"{self.t1.__str__()} | {self.t2.__str__()}"


@final
class NullableType[T: RenkonType](RenkonType):
    def __init__(self, t: T):
        super().__init__()
        self.t = t

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other) and self.t == other.t

    def __gt__(self, other: RenkonType) -> bool:
        """A? > B if A > B, and A? > A."""
        return self.t > other

    def __lt__(self, other: RenkonType) -> bool:
        return False

    @property
    def code(self) -> str:
        return f"{self.t.__str__()}?"

    # def nullable(self) -> NullableType[T]:
    #     return self


@final
class IntType(PrimitiveType):
    from_polars = list(pl.INTEGER_DTYPES)
    to_polars = pl.Int64
    from_python = [int]
    to_python = int

    @property
    def code(self) -> str:
        return "int"


@final
class FloatType(PrimitiveType):
    from_polars = pl.FLOAT_DTYPES
    to_polars = pl.Float64
    from_python = [float]
    to_python = float

    @property
    def code(self) -> str:
        return "float"


@final
class StringType(PrimitiveType):
    from_polars = [pl.Utf8]
    to_polars = pl.Utf8
    from_python = [str]
    to_python = str

    @property
    def code(self) -> str:
        return "string"


@final
class BooleanType(PrimitiveType):
    from_polars = [pl.Boolean]
    to_polars = pl.Boolean
    from_python = [bool]
    to_python = bool

    @property
    def code(self) -> str:
        return "bool"


def test_serde():
    ta = TypeAdapter(RenkonType)
    int_type = TypeSystem.int_type()

    assert TypeSystem.to_polars(int_type) == pl.Int64
    assert TypeSystem.to_python(int_type) == int

    # Conversion from python type
    assert ta.validate_python(int_type) == int_type

    # Conversion from code
    assert ta.validate_python("int") == int_type
    assert ta.validate_json('"int"') == int_type

    # Conversion from all supported polars types
    for polars_type in pl.INTEGER_DTYPES:
        assert ta.validate_python(polars_type) == int_type

    with pytest.raises(ValueError, match="not convertible to a Renkon type"):
        ta.validate_python(pl.Decimal)
        ta.validate_python(list)


def test_primitive_type_equality():
    int_type = TypeSystem.int_type()
    float_type = TypeSystem.float_type()
    string_type = TypeSystem.string_type()
    bool_type = TypeSystem.boolean_type()

    prim_types = [int_type, float_type, string_type, bool_type]

    for prim_type in prim_types:
        assert prim_type == prim_type
        for other_prim_type in set(prim_types) - {prim_type}:
            assert prim_type != other_prim_type


def test_union_type_subtyping():
    int_type = TypeSystem.int_type()
    float_type = TypeSystem.float_type()
    string_type = TypeSystem.string_type()
    bool_type = TypeSystem.boolean_type()

    prim_types = [int_type, float_type, string_type, bool_type]

    for prim_type_a in prim_types:
        for prim_type_b in prim_types:
            union_type = prim_type_a.union(prim_type_b)

            assert union_type == union_type
            assert prim_type_a != union_type
            assert prim_type_b != union_type

            assert prim_type_a < union_type
            assert prim_type_b < union_type
            assert prim_type_a <= union_type
            assert prim_type_b <= union_type

            assert union_type > prim_type_a
            assert union_type > prim_type_b
            assert union_type >= prim_type_a
            assert union_type >= prim_type_b


def test_nullable_type_equality():
    int_type = TypeSystem.int_type()
    float_type = TypeSystem.float_type()
    string_type = TypeSystem.string_type()
    bool_type = TypeSystem.boolean_type()

    prim_types = [int_type, float_type, string_type, bool_type]

    for prim_type in prim_types:
        assert prim_type.nullable() == prim_type.nullable()
        assert prim_type.nullable() == NullableType(prim_type)
        assert prim_type.nullable() == prim_type.nullable().nullable()
        assert prim_type.nullable() != int_type
        assert prim_type.nullable() != float_type
        assert prim_type.nullable() != string_type
        assert prim_type.nullable() != bool_type
