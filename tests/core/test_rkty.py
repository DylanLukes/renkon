import pyarrow as pa

from renkon.core import types
from renkon.core.types import Type


def test_this_crap() -> None:
    assert Type.from_py(int) == types.int64
    assert Type.from_py(float) == types.float64
    assert Type.from_py(str) == types.string
    assert Type.from_py(bool) == types.bool_

    assert Type.from_arrow(pa.uint8()) == types.uint8
    assert Type.from_arrow(pa.uint16()) == types.uint16
    assert Type.from_arrow(pa.uint32()) == types.uint32
    assert Type.from_arrow(pa.uint64()) == types.uint64
    assert Type.from_arrow(pa.int8()) == types.int8
    assert Type.from_arrow(pa.int16()) == types.int16
    assert Type.from_arrow(pa.int32()) == types.int32
    assert Type.from_arrow(pa.int64()) == types.int64
    assert Type.from_arrow(pa.float16()) == types.float16
    assert Type.from_arrow(pa.float32()) == types.float32
    assert Type.from_arrow(pa.float64()) == types.float64
    assert Type.from_arrow(pa.bool_()) == types.bool_
    assert Type.from_arrow(pa.string()) == types.string
