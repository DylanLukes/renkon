# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Annotated, Any, TypedDict, TypeGuard

import polars as pl
import pyarrow as pa
from annotated_types import Predicate
from polars import Series
from pydantic import Base64Bytes, PositiveInt, TypeAdapter
from pydantic_core import core_schema as cs

if TYPE_CHECKING:
    from pydantic import (
        GetCoreSchemaHandler,
        GetJsonSchemaHandler,
    )
    from pydantic.json_schema import JsonSchemaValue
    from pydantic_core.core_schema import CoreSchema


def is_bit_series(s: Series) -> TypeGuard[BitSeries]:
    return s.dtype.is_(pl.Boolean)


type BitSeries = Annotated[Series, Predicate(is_bit_series), _BitSeriesPydanticAnnotation]


class _BitSeriesFields(TypedDict):
    """
    :param length: the number of bits in the series.
    :param data: the raw data of the series.
    """

    length: PositiveInt
    data: Base64Bytes


def _validate_bitseries_from_fields(b: _BitSeriesFields) -> BitSeries:
    count = b["length"]
    data = b["data"]

    if not len(data) * 8 >= count:
        msg = f"Data length {len(data)} is insufficient to contain {count} bits."
        raise ValueError(msg)

    buf = pa.py_buffer(data)
    arr = pa.Array.from_buffers(pa.bool_(), length=count, buffers=[None, buf])
    return pl.Series(arr, dtype=pl.Boolean)


def _validate_bitseries_from_series(s: Series) -> BitSeries:
    if not is_bit_series(s):
        msg = "Series is not a boolean series."
        raise TypeError(msg)
    return s


def _serialize_bitseries_to_fields(s: BitSeries) -> _BitSeriesFields:
    count = len(s)
    data = base64.encodebytes(s.to_arrow().buffers()[1].to_pybytes())
    return _BitSeriesFields(length=count, data=data)


class _BitSeriesPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> CoreSchema:
        typed_dict_schema = TypeAdapter(_BitSeriesFields).core_schema

        json_schema = cs.chain_schema(
            [typed_dict_schema, cs.no_info_plain_validator_function(_validate_bitseries_from_fields)]
        )

        py_schema = cs.chain_schema(
            [
                cs.is_instance_schema(Series),
                cs.no_info_plain_validator_function(_validate_bitseries_from_series),
            ]
        )

        serializer = cs.plain_serializer_function_ser_schema(_serialize_bitseries_to_fields)

        return cs.json_or_python_schema(json_schema=json_schema, python_schema=py_schema, serialization=serializer)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return handler(core_schema)


# if __name__ == "__main__":
#     import numpy as np
#     import polars as pl
#     from pydantic import BaseModel
#
#
#     class Model(BaseModel):
#         mask: BitSeries
#
#
#     data = np.packbits(np.random.randint(0, 2, 1000).astype(bool)).tobytes()
#     print(len(data))
#
#     fields = _BitSeriesFields(length=1000, data=data)
#     ta = TypeAdapter(_BitSeriesFields)
#     print(ta.core_schema)
#
#     ta.validate_python(ta.dump_python(fields))
#
#     buf = pa.py_buffer(data)
#     arr = pa.Array.from_buffers(pa.bool_(), 1000, [None, buf])
#     mask = pl.Series("mask", arr)
#     assert is_bit_series(mask)
#     # print(mask)
#
#     model = Model(mask=mask)
#     print(model.model_dump_json())
#     roundtripped = Model.model_validate_json(model.model_dump_json())
