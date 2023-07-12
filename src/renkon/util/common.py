from __future__ import annotations

import re
from typing import NoReturn, cast

import pyarrow as pa


def unreachable() -> NoReturn:
    msg = "unreachable"
    raise AssertionError(msg)


SUP = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
}

SUB = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
}

SUP_RE = re.compile(r"(?:\^|\^{)([0-9]+)}?")
SUB_RE = re.compile(r"(?:_|_{)([0-9]+)}?")


def pretty_sup(s: str) -> str:  # pragma: no cover
    """
    Format pretty superscripts in a string. For example:
      -  x^2 -> x²
      - x^{123} -> x¹²³
    """
    for match in SUP_RE.finditer(s):
        old = match.group(0)
        new = "".join(SUP.get(c, c) for c in match.group(1))
        s = s.replace(old, new)
    return s


def pretty_sub(s: str) -> str:  # pragma: no cover
    """
    Format pretty subscripts in a string. For example:
      -  x_2 -> x₂
      - x_{123} -> x₁₂₃
    """
    for match in SUB_RE.finditer(s):
        old = match.group(0)
        new = "".join(SUB.get(c, c) for c in match.group(1))
        s = s.replace(old, new)
    return s


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
