from pyarrow import lib as pal

from renkon.core import rkty
from renkon.core.rkty import RkTy


def test_this_crap() -> None:
    assert RkTy.from_py(bool) == rkty.bool_()
    assert RkTy.from_py(int) == rkty.sint64()
    assert RkTy.from_py(float) == rkty.float64()
    assert RkTy.from_py(str) == rkty.string()

    assert RkTy.from_arrow(pal.uint8()) == rkty.uint8()
    assert RkTy.from_arrow(pal.uint16()) == rkty.uint16()
    assert RkTy.from_arrow(pal.uint32()) == rkty.uint32()
    assert RkTy.from_arrow(pal.uint64()) == rkty.uint64()
    assert RkTy.from_arrow(pal.int8()) == rkty.sint8()
    assert RkTy.from_arrow(pal.int16()) == rkty.sint16()
    assert RkTy.from_arrow(pal.int32()) == rkty.sint32()
    assert RkTy.from_arrow(pal.int64()) == rkty.sint64()
    assert RkTy.from_arrow(pal.float16()) == rkty.float16()
    assert RkTy.from_arrow(pal.float32()) == rkty.float32()
    assert RkTy.from_arrow(pal.float64()) == rkty.float64()
    assert RkTy.from_arrow(pal.bool_()) == rkty.bool_()
    assert RkTy.from_arrow(pal.string()) == rkty.string()
