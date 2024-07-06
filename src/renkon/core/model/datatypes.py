# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, final, override

from polars import PolarsDataType

from renkon.util.singleton import Singleton, singletonmethod

if TYPE_CHECKING:
    from polars.type_aliases import PythonDataType


class TypeSystem(Singleton):
    """
    Represents the entire Renkon data type system. This is a singleton rather than module-level
    state to allow for easy extension and testing of the data type system in the future.
    """

    _code_to_type: dict[str, Type] = {}
    _type_to_code: dict[Type, str] = {}

    _rk_to_pl: dict[Type, PolarsDataType] = {}
    _pl_to_rk: dict[PolarsDataType, Type] = {}

    _rk_to_py: dict[Type, PythonDataType] = {}
    _py_to_rk: dict[PythonDataType, Type] = {}

    @singletonmethod
    def register_primitive_type(self, rkty: Type, code: str) -> None:
        if rkty in self._type_to_code:
            msg = f"Type {rkty} is already registered to code {self._type_to_code[rkty]}"
            raise KeyError(msg)
        if code in self._code_to_type:
            msg = f"Code {code} is already registered to type {self._code_to_type[code]}"
            raise KeyError(msg)

        self._code_to_type[code] = rkty
        self._type_to_code[rkty] = code


type RenkonType = PrimitiveType | UnionType[Type, Type]


class Type(ABC):
    @abstractmethod
    def type_code(self) -> str:
        ...


class PrimitiveType(Type, ABC, Singleton):
    @singletonmethod
    @abstractmethod
    def type_code(self) -> str:
        ...


class UnionType[T1: Type, T2: Type](Type, ABC):
    @override
    def type_code(self) -> str:
        ...


@final
class Int(PrimitiveType):
    @override
    def type_code(self) -> str:
        return "int"

# @final
# class String(PrimitiveType):
#     ...

# class DataTypePydanticMixin:
#     code: str
#
# @classmethod
# def __get_pydantic_core_schema__(
#         cls,
#         _source_type: Any,
#         _handler: GetCoreSchemaHandler
# ) -> CoreSchema:
#     # fmt: off
#     def validate_from_code(code: str) -> RenkonDataType:
#         return cls.__code_to_type__[code]
#
#     def serialize_to_code(dt: RenkonDataType) -> str:
#         return cls.__type_to_code__[dt]
#
#     from_code_schema = core_schema.chain_schema([
#         core_schema.str_schema(),
#         core_schema.no_info_plain_validator_function(validate_from_code),
#     ])
#
#     return core_schema.json_or_python_schema(
#         json_schema=from_code_schema,
#         python_schema=core_schema.union_schema([
#             core_schema.is_instance_schema(DataTypeClass),
#             core_schema.is_instance_schema(PrimitiveDataType),
#             from_code_schema
#         ]),
#         serialization=core_schema.plain_serializer_function_ser_schema(serialize_to_code)
#     )
#         # fmt: on
#
#     @classmethod
#     def __get_pydantic_json_schema__(
#             cls,
#             _core_schema: core_schema.CoreSchema,
#             handler: GetJsonSchemaHandler
#     ):
#         return handler(core_schema.str_schema())

# class DataTypeClass(type):
#     """
#     A metaclass for defining and registering Renkon data types. Provides:
#
#     - A registry of Renkon data types and their corresponding codes.
#     - A matching __repr__ method for Renkon data types.
#     """
#
#     @classmethod
#     def register_type(
#             cls,  # mcls
#             type_: DataTypeClass,
#             code: str,
#             from_polars: Iterable[PolarsDataType],
#             into_polars: PolarsDataType,
#             from_python: Iterable[PythonDataType],
#             into_python: PythonDataType
#     ):
#         mcls = cls  # for clarity + appeasing pyright
#         tysys = TypeSystem.singleton()
#
#         if not issubclass(type_, PrimitiveDataType):
#             raise TypeError(f"Class {type_} must be a subclass of DataType")
#
#         mcls.__code_to_type__[code] = type_
#         mcls.__type_to_code__[type_] = code
#
#         for polars_type in from_polars:
#             if polars_type in mcls.__pl_to_rk__:
#                 msg = f"Polars type {polars_type} is already mapped to a RenkonDataTypeClass"
#                 raise ValueError(msg)
#             type_.__pl_to_rk__[polars_type] = type_
#
#         return type_
#
#     def __repr__(cls) -> str:
#         return f"Rk{cls.__name__}"
#
#     @classmethod
#     def __get_pydantic_core_schema__(
#             cls,
#             _source_type: Any,
#             _handler: GetCoreSchemaHandler
#     ) -> CoreSchema:
#         # fmt: off
#         def validate_from_code(code: str) -> RenkonDataType:
#             return cls.__code_to_type__[code]
#
#         def serialize_to_code(dt: RenkonDataType) -> str:
#             return cls.__type_to_code__[dt]
#
#         from_code_schema = core_schema.chain_schema([
#             core_schema.str_schema(),
#             core_schema.no_info_plain_validator_function(validate_from_code),
#         ])
#
#         return core_schema.json_or_python_schema(
#             json_schema=from_code_schema,
#             python_schema=core_schema.union_schema([
#                 core_schema.is_instance_schema(DataTypeClass),
#                 core_schema.is_instance_schema(PrimitiveDataType),
#                 from_code_schema
#             ]),
#             serialization=core_schema.plain_serializer_function_ser_schema(serialize_to_code)
#         )
#         # fmt: on
#
#     @classmethod
#     def __get_pydantic_json_schema__(
#             cls,
#             _core_schema: core_schema.CoreSchema,
#             handler: GetJsonSchemaHandler
#     ):
#         return handler(core_schema.str_schema())
#
#
# class ProductDataType(metaclass=DataTypeClass):
#     pass
#
#
# class PrimitiveDataType(metaclass=DataTypeClass):
#     code: ClassVar[str]
#
#     def __init_subclass__(
#             cls,
#             code: str,
#             from_polars: Iterable[PolarsDataType],
#             into_polars: PolarsDataType,
#             from_python: Iterable[PythonDataType],
#             into_python: PythonDataType,
#             *args: Any,
#             **kwargs: Any,
#     ):
#         DataTypeClass.register_type(cls, code, from_polars, into_polars, from_python, into_python)
#         super().__init_subclass__(*args, **kwargs)
#
#     def __eq__(self, other: RenkonDataType):  # type: ignore[override]
#         if type(other) is DataTypeClass:
#             return issubclass(other, type(self))
#         else:
#             return isinstance(other, type(self))
#
#     def __hash__(self):
#         return hash(self.__class__)
#
#     def __repr__(self):
#         return f"Rk{self.__class__.__name__}"
#
#     @classmethod
#     def from_polars(cls, polars_type: PolarsDataType) -> RenkonDataType:
#         return DataTypeClass.__pl_to_rk__[polars_type]
#
#
# # region: Canonical DataTypes
# # fmt: off
#
# class Int(
#     PrimitiveDataType,
#     code="int",
#     from_polars=pldt.INTEGER_DTYPES,
#     into_polars=pldt.Int64,
#     from_python={int},
#     into_python=int
# ): ...
#
#
# class Float(
#     PrimitiveDataType,
#     code="float",
#     from_polars=pldt.FLOAT_DTYPES,
#     into_polars=pldt.Float64,
#     from_python={float},
#     into_python=float,
# ): ...
#
#
# class String(
#     PrimitiveDataType,
#     code="str",
#     from_polars={pldt.Utf8},
#     into_polars=pldt.Utf8,
#     from_python={str},
#     into_python=str
# ): ...
#
#
# class Bool(
#     PrimitiveDataType,
#     code="bool",
#     from_polars={pldt.Boolean},
#     into_polars=pldt.Boolean,
#     from_python={bool},
#     into_python=bool
# ): ...
#
#
# class Binary(
#     PrimitiveDataType, code="bin",
#     from_polars={pldt.Binary},
#     into_polars=pldt.Binary,
#     from_python={bytes},
#     into_python=bytes
# ): ...
#
#
# class Date(
#     PrimitiveDataType,
#     code="date",
#     from_polars={pldt.Date},
#     into_polars=pldt.Date,
#     from_python={datetime.date},
#     into_python=datetime.date,
# ): ...
#
#
# class Time(
#     PrimitiveDataType,
#     code="time",
#     from_polars={pldt.Time},
#     into_polars=pldt.Time,
#     from_python={datetime.time},
#     into_python=datetime.time,
# ): ...
#
#
# class Datetime(
#     PrimitiveDataType,
#     code="datetime",
#     from_polars={pldt.Datetime},
#     into_polars=pldt.Datetime,
#     from_python={datetime.datetime},
#     into_python=datetime.datetime,
# ): ...
#
#
# ALL_TYPES = [
#     Int,
#     Float,
#     String,
#     Bool,
#     Binary,
#     Date,
#     Time,
#     Datetime,
# ]
#
# # fmt: on
# # endregion
#
# if __name__ == "__main__":
#     ta_inst = TypeAdapter(PrimitiveDataType)
#     assert Int() == ta_inst.validate_json(ta_inst.dump_json(Int()))
#
#     ta_type = TypeAdapter(type(PrimitiveDataType))
#     assert Int == ta_type.validate_json(ta_type.dump_json(Int))
#
#     assert ta_inst.dump_json(Int()) == ta_type.dump_json(Int)
#     assert ta_inst.validate_json(ta_type.dump_json(Int)) == ta_type.validate_json(ta_type.dump_json(Int))
#
#     assert Int == Int
#     assert Int == Int()
#     assert Int != Float
#     assert Int != Float()
