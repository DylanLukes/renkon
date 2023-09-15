from typing import cast

import pyarrow as pa


def serialize_schema(schema: pa.Schema) -> bytes:
    """
    Serialize a schema to bytes.
    """
    return cast(bytes, schema.serialize().to_pybytes())


def deserialize_schema(blob: bytes) -> pa.Schema:
    """
    Deserialize a schema from bytes.
    """
    return pa.ipc.read_schema(pa.py_buffer(blob))
