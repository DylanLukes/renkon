from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, Literal, TypeAlias, TypeVar, overload

import pyarrow as pa

from renkon.core.rkty import (
    RkAnyTy,
    RkBoolTy,
    RkFloat16Ty,
    RkFloat32Ty,
    RkFloat64Ty,
    RkFloatTy,
    RkIntTy,
    RkSInt8Ty,
    RkSInt16Ty,
    RkSInt32Ty,
    RkSInt64Ty,
    RkStringTy,
    RkTy,
    RkUInt8Ty,
    RkUInt16Ty,
    RkUInt32Ty,
    RkUInt64Ty,
)


class Filled(Enum):
    NO = False
    YES = True


_RkTy_Co = TypeVar("_RkTy_Co", bound=RkAnyTy, covariant=True)
_RkTy = TypeVar("_RkTy", bound=RkAnyTy, covariant=False)
_IsFilled = TypeVar("_IsFilled", bound=Filled, covariant=True)


@dataclass(frozen=True, slots=True)
class Hole(Generic[_RkTy_Co, _IsFilled]):
    """
    Represents a hole in a Renkon sketch. A hole has a name and an allowed type.
    """

    name: str
    _type: _RkTy_Co
    _value: int | float | str | bool | None = None

    @staticmethod
    def empty(name: str, rk_type: _RkTy) -> Hole[_RkTy, Literal[Filled.NO]]:
        return Hole(name, rk_type, None)

    @staticmethod
    @overload
    def from_py(name: str, py_value: bool) -> Hole[RkBoolTy, Literal[Filled.YES]]:  # type: ignore  # noqa: FBT001
        ...

    @staticmethod
    @overload
    def from_py(name: str, py_value: int) -> Hole[RkIntTy, Literal[Filled.YES]]:
        ...

    @staticmethod
    @overload
    def from_py(name: str, py_value: float) -> Hole[RkFloatTy, Literal[Filled.YES]]:
        ...

    @staticmethod
    @overload
    def from_py(name: str, py_value: str) -> Hole[RkStringTy, Literal[Filled.YES]]:
        ...

    @staticmethod
    def from_py(name: str, py_value: int | float | str | bool) -> Hole[RkAnyTy, Literal[Filled.YES]]:
        rk_type = RkTy.from_py(type(py_value))
        if rk_type is None:
            msg = f"Cannot convert to Renkon type from Python type {type(py_value)}"
            raise ValueError(msg)
        return Hole(name, rk_type, py_value)

    @overload
    def py_value(self: Hole[RkIntTy, Literal[Filled.YES]]) -> int:
        ...

    @overload
    def py_value(self: Hole[RkFloatTy, Literal[Filled.YES]]) -> float:
        ...

    @overload
    def py_value(self: Hole[RkStringTy, Literal[Filled.YES]]) -> str:
        ...

    @overload
    def py_value(self: Hole[RkBoolTy, Literal[Filled.YES]]) -> bool:
        ...

    def py_value(self) -> int | float | str | bool | None:
        return self._value

    @overload
    def arrow_value(self: Hole[RkFloat16Ty, Literal[Filled.NO]]) -> None:
        ...

    @overload
    def arrow_value(self: Hole[RkUInt8Ty, Literal[Filled.YES]]) -> pa.UInt8Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkUInt16Ty, Literal[Filled.YES]]) -> pa.UInt16Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkUInt32Ty, Literal[Filled.YES]]) -> pa.UInt32Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkUInt64Ty, Literal[Filled.YES]]) -> pa.UInt64Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkSInt8Ty, Literal[Filled.YES]]) -> pa.Int8Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkSInt16Ty, Literal[Filled.YES]]) -> pa.Int16Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkSInt32Ty, Literal[Filled.YES]]) -> pa.Int32Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkSInt64Ty, Literal[Filled.YES]]) -> pa.Int64Scalar:
        ...

    @overload
    def arrow_value(self: Hole[RkFloat16Ty, Literal[Filled.YES]]) -> pa.HalfFloatScalar:
        ...

    @overload
    def arrow_value(self: Hole[RkFloat32Ty, Literal[Filled.YES]]) -> pa.FloatScalar:
        ...

    @overload
    def arrow_value(self: Hole[RkFloat64Ty, Literal[Filled.YES]]) -> pa.DoubleScalar:
        ...

    @overload
    def arrow_value(self: Hole[RkStringTy, Literal[Filled.YES]]) -> pa.StringScalar:
        ...

    @overload
    def arrow_value(self: Hole[RkBoolTy, Literal[Filled.YES]]) -> pa.BooleanScalar:
        ...

    def arrow_value(self) -> pa.Scalar | None:
        return pa.scalar(self._value, type=self._type.as_arrow())

    @overload
    def is_filled(self: Hole[RkAnyTy, Literal[Filled.YES]]) -> Literal[True]:
        ...

    @overload
    def is_filled(self: Hole[RkAnyTy, Literal[Filled.NO]]) -> Literal[False]:
        ...

    def is_filled(self: Hole[RkAnyTy, Literal[Filled.YES]]) -> bool:
        return self._value is not None
