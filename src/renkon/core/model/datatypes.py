# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any, ClassVar

from polars import PolarsDataType
from polars import datatypes as pldt
from polars.datatypes.classes import classinstmethod
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic_core import core_schema, CoreSchema

if TYPE_CHECKING:
    from collections.abc import Iterable

    from polars.type_aliases import PythonDataType

    from renkon.core.model.type_aliases import RenkonDataType


class DataTypeClass(type):
    __code_to_type__: ClassVar[dict[str, RenkonDataType]] = {}
    __type_to_code__: ClassVar[dict[RenkonDataType, str]] = {}

    __rk_to_pl__: ClassVar[dict[RenkonDataType, PolarsDataType]] = {}
    __pl_to_rk__: ClassVar[dict[PolarsDataType, RenkonDataType]] = {}

    __rk_to_py__: ClassVar[dict[RenkonDataType, PythonDataType]] = {}
    __py_to_rk__: ClassVar[dict[PythonDataType, RenkonDataType]] = {}

    @classmethod
    def register_type(
            cls,  # mcls
            type_: DataTypeClass,
            code: str,
            from_polars: Iterable[PolarsDataType],
            into_polars: PolarsDataType,
            from_python: Iterable[PythonDataType],
            into_python: PythonDataType
    ):
        mcls = cls  # for clarity + appeasing pyright

        if not issubclass(type_, DataType):
            raise TypeError(f"Class {type_} must be a subclass of DataType")

        mcls.__code_to_type__[code] = type_
        mcls.__type_to_code__[type_] = code

        for polars_type in from_polars:
            if polars_type in mcls.__pl_to_rk__:
                msg = f"Polars type {polars_type} is already mapped to a RenkonDataTypeClass"
                raise ValueError(msg)
            type_.__pl_to_rk__[polars_type] = type_

        return type_

    def __repr__(cls) -> str:
        return f"Rk{cls.__name__}"

    # For the benefit of the typechecker only...
    @classmethod
    def from_polars(cls, polars_type: PolarsDataType) -> RenkonDataType:
        ...

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        # fmt: off
        def validate_from_code(code: str) -> RenkonDataType:
            return cls.__code_to_type__[code]

        def serialize_to_code(dt: RenkonDataType) -> str:
            return cls.__type_to_code__[dt]

        from_code_schema = core_schema.chain_schema([
            core_schema.str_schema(),
            core_schema.no_info_plain_validator_function(validate_from_code),
        ])

        return core_schema.json_or_python_schema(
            json_schema=from_code_schema,
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(DataTypeClass),
                core_schema.is_instance_schema(DataType),
                from_code_schema
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(serialize_to_code)
        )
        # fmt: on

    @classmethod
    def __get_pydantic_json_schema__(
            cls,
            _core_schema: core_schema.CoreSchema,
            handler: GetJsonSchemaHandler
    ):
        return handler(core_schema.str_schema())


class DataType(metaclass=DataTypeClass):
    code: ClassVar[str]

    def __init_subclass__(
            cls,
            code: str,
            from_polars: Iterable[PolarsDataType],
            into_polars: PolarsDataType,
            from_python: Iterable[PythonDataType],
            into_python: PythonDataType,
            *args: Any,
            **kwargs: Any,
    ):
        DataTypeClass.register_type(cls, code, from_polars, into_polars, from_python, into_python)
        super().__init_subclass__(*args, **kwargs)

    def __eq__(self, other: RenkonDataType):  # type: ignore[override]
        if type(other) is DataTypeClass:
            return issubclass(other, type(self))
        else:
            return isinstance(other, type(self))

    def __hash__(self):
        return hash(self.__class__)

    def __repr__(self):
        return f"Rk{self.__class__.__name__}"

    @classinstmethod
    def from_polars(self, polars_type: PolarsDataType) -> RenkonDataType:
        return DataTypeClass.__pl_to_rk__[polars_type]


# Conversion Methods
def tyconv_polars_to_renkon(polars_type: PolarsDataType) -> RenkonDataType:
    return DataType.__pl_to_rk__[polars_type]


def tyconv_renkon_to_polars(renkon_type: RenkonDataType) -> PolarsDataType:
    return DataType.__rk_to_pl__[renkon_type]


# region: Concrete DataTypes
# fmt: off

class Int(
    DataType,
    code="int",
    from_polars=pldt.INTEGER_DTYPES,
    into_polars=pldt.Int64,
    from_python={int},
    into_python=int
): ...


class Float(
    DataType,
    code="float",
    from_polars=pldt.FLOAT_DTYPES,
    into_polars=pldt.Float64,
    from_python={float},
    into_python=float,
): ...


class String(
    DataType,
    code="str",
    from_polars={pldt.Utf8},
    into_polars=pldt.Utf8,
    from_python={str},
    into_python=str
): ...


class Bool(
    DataType,
    code="bool",
    from_polars={pldt.Boolean},
    into_polars=pldt.Boolean,
    from_python={bool},
    into_python=bool
): ...


class Binary(
    DataType, code="bin",
    from_polars={pldt.Binary},
    into_polars=pldt.Binary,
    from_python={bytes},
    into_python=bytes
): ...


class Date(
    DataType,
    code="date",
    from_polars={pldt.Date},
    into_polars=pldt.Date,
    from_python={datetime.date},
    into_python=datetime.date,
): ...


class Time(
    DataType,
    code="time",
    from_polars={pldt.Time},
    into_polars=pldt.Time,
    from_python={datetime.time},
    into_python=datetime.time,
): ...


class Datetime(
    DataType,
    code="datetime",
    from_polars={pldt.Datetime},
    into_polars=pldt.Datetime,
    from_python={datetime.datetime},
    into_python=datetime.datetime,
): ...

ALL_TYPES = [
    Int,
    Float,
    String,
    Bool,
    Binary,
    Date,
    Time,
    Datetime,
]

# fmt: on
# endregion

if __name__ == "__main__":
    ta_inst = TypeAdapter(DataType)
    assert Int() == ta_inst.validate_json(ta_inst.dump_json(Int()))

    ta_type = TypeAdapter(type(DataType))
    assert Int == ta_type.validate_json(ta_type.dump_json(Int))

    assert ta_inst.dump_json(Int()) == ta_type.dump_json(Int)
    assert ta_inst.validate_json(ta_type.dump_json(Int)) == ta_type.validate_json(ta_type.dump_json(Int))

    assert Int == Int
    assert Int == Int()
    assert Int != Float
    assert Int != Float()