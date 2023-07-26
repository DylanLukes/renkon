from __future__ import annotations

from typing import Any, NoReturn, TypeVar, cast

import pyarrow as pa


def unreachable() -> NoReturn:  # pragma: no cover
    msg = "unreachable"
    raise AssertionError(msg)


T = TypeVar("T")


def checked_cast(typ: type[T], val: Any) -> T:  # pragma: no cover
    """
    Cast an object to a type, using MyPy's type checker to ensure the cast is valid,
    BUT also using a runtime check to ensure the cast is valid. Adds a tiny bit of
    overhead, but during development helps catch bugs where they are introduced
    rather than later when some operation using them blows up.
    """
    if not isinstance(val, typ):
        msg = f"expected {typ}, got {type(val)}"
        raise TypeError(msg)
    return cast(T, val)  # type: ignore[redundant-cast]


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
