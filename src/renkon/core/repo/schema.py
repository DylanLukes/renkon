# pyright: basic
"""
This module contains some ugly hacks to work around the fact that PyArrow
is untypes, and we want to strictly type. So, we constraint the ugly bits
that require Pyright to run in basic mode to this file.
"""
from typing import cast

import polars as pl
import pyarrow as pa
from polars import DataFrame

from renkon.core.type_aliases import Schema


def to_arrow_schema_bytes(schema: Schema) -> bytes:
    """
    Serialize a schema to bytes.
    """
    arrow_schema = DataFrame(schema=schema).to_arrow().schema
    return cast(bytes, arrow_schema.serialize().to_pybytes())


def from_arrow_schema_bytes(blob: bytes) -> Schema:
    """
    Deserialize a schema from bytes.
    """
    arrow_schema = pa.ipc.read_schema(pa.py_buffer(blob))
    return dict(cast(DataFrame, pl.from_arrow(pa.table([], schema=arrow_schema))).schema)
