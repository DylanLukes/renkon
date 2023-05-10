from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, auto
from typing import Generic, Literal, NewType, NoReturn, TypeGuard, TypeVar, final

import pyarrow.lib as pal


@final
class Repr(Flag):
    UINT = auto()
    SINT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOL = auto()


@final
class Width(Flag):
    BIT = 1
    BYTE = 8
    WORD = 16
    DWORD = 32
    QWORD = 64
    VARIABLE = auto()


_Repr = TypeVar("_Repr", bound=Repr, covariant=True)
_Width = TypeVar("_Width", bound=Width, covariant=True)


def unreachable() -> NoReturn:
    msg = "unreachable"
    raise AssertionError(msg)


@dataclass(frozen=True, slots=True)
class RkTy(Generic[_Repr, _Width]):
    repr_: _Repr
    width: _Width

    def as_py(self) -> type:
        match (self.repr_, self.width):
            case (Repr.UINT, _):
                return int
            case (Repr.SINT, _):
                return int
            case (Repr.FLOAT, _):
                return float
            case (Repr.STRING, _):
                return str
            case (Repr.BOOL, _):
                return bool
            case _:
                unreachable()

    @staticmethod
    def from_py(
        py_type: type,
    ) -> RkAnyTy | None:
        match py_type:
            case _ if py_type is int:
                return sint64()
            case _ if py_type is float:
                return float64()
            case _ if py_type is str:
                return string()
            case _ if py_type is bool:
                return bool_()
        return None

    def as_arrow(
        self,
    ) -> pal.DataType:
        match self.repr_:
            case Repr.UINT:
                match self.width:
                    case Width.BYTE:
                        return pal.uint8()
                    case Width.WORD:
                        return pal.uint16()
                    case Width.DWORD:
                        return pal.uint32()
                    case Width.QWORD:
                        return pal.uint64()
                    case _:
                        unreachable()
            case Repr.SINT:
                match self.width:
                    case Width.BYTE:
                        return pal.int8()
                    case Width.WORD:
                        return pal.int16()
                    case Width.DWORD:
                        return pal.int32()
                    case Width.QWORD:
                        return pal.int64()
                    case _:
                        unreachable()
            case Repr.FLOAT:
                match self.width:
                    case Width.BYTE | Width.WORD:
                        return pal.float16()
                    case Width.DWORD:
                        return pal.float32()
                    case Width.QWORD:
                        return pal.float64()
                    case _:
                        unreachable()
            case Repr.STRING:
                return pal.string()
            case Repr.BOOL:
                return pal.bool_()
            case _:
                unreachable()

    @staticmethod
    def from_arrow(arrow_type: pal.DataType) -> RkTy[Repr, Width] | None:
        match arrow_type.id:
            case pal.Type_UINT8:
                return RkTy(Repr.UINT, Width.BYTE)
            case pal.Type_UINT16:
                return RkTy(Repr.UINT, Width.WORD)
            case pal.Type_UINT32:
                return RkTy(Repr.UINT, Width.DWORD)
            case pal.Type_UINT64:
                return RkTy(Repr.UINT, Width.QWORD)
            case pal.Type_INT8:
                return RkTy(Repr.SINT, Width.BYTE)
            case pal.Type_INT16:
                return RkTy(Repr.SINT, Width.WORD)
            case pal.Type_INT32:
                return RkTy(Repr.SINT, Width.DWORD)
            case pal.Type_INT64:
                return RkTy(Repr.SINT, Width.QWORD)
            case pal.Type_HALF_FLOAT:
                return RkTy(Repr.FLOAT, Width.WORD)
            case pal.Type_FLOAT:
                return RkTy(Repr.FLOAT, Width.DWORD)
            case pal.Type_DOUBLE:
                return RkTy(Repr.FLOAT, Width.QWORD)
            case pal.Type_STRING:
                return RkTy(Repr.STRING, Width.VARIABLE)
            case pal.Type_BOOL:
                return RkTy(Repr.BOOL, Width.BIT)
            case _:
                return None


RkBoolTy = NewType("RkBoolTy", RkTy[Literal[Repr.BOOL], Literal[Width.BIT]])

RkUInt8Ty = NewType("RkUInt8Ty", RkTy[Literal[Repr.UINT], Literal[Width.BYTE]])
RkUInt16Ty = NewType("RkUInt16Ty", RkTy[Literal[Repr.UINT], Literal[Width.WORD]])
RkUInt32Ty = NewType("RkUInt32Ty", RkTy[Literal[Repr.UINT], Literal[Width.DWORD]])
RkUInt64Ty = NewType("RkUInt64Ty", RkTy[Literal[Repr.UINT], Literal[Width.QWORD]])
RkUIntTy = RkUInt8Ty | RkUInt16Ty | RkUInt32Ty | RkUInt64Ty

RkSInt8Ty = NewType("RkSInt8Ty", RkTy[Literal[Repr.SINT], Literal[Width.BYTE]])
RkSInt16Ty = NewType("RkSInt16Ty", RkTy[Literal[Repr.SINT], Literal[Width.WORD]])
RkSInt32Ty = NewType("RkSInt32Ty", RkTy[Literal[Repr.SINT], Literal[Width.DWORD]])
RkSInt64Ty = NewType("RkSInt64Ty", RkTy[Literal[Repr.SINT], Literal[Width.QWORD]])
RkSIntTy = RkSInt8Ty | RkSInt16Ty | RkSInt32Ty | RkSInt64Ty

RkIntTy = RkUIntTy | RkSIntTy

RkFloat16Ty = NewType("RkFloat16Ty", RkTy[Literal[Repr.FLOAT], Literal[Width.WORD]])
RkFloat32Ty = NewType("RkFloat32Ty", RkTy[Literal[Repr.FLOAT], Literal[Width.DWORD]])
RkFloat64Ty = NewType("RkFloat64Ty", RkTy[Literal[Repr.FLOAT], Literal[Width.QWORD]])
RkFloatTy = RkFloat16Ty | RkFloat32Ty | RkFloat64Ty

RkNumberTy = RkIntTy | RkFloatTy

RkStringTy = NewType("RkStringTy", RkTy[Literal[Repr.STRING], Literal[Width.VARIABLE]])

RkAnyTy = RkBoolTy | RkNumberTy | RkStringTy | RkBoolTy


def uint8() -> RkUInt8Ty:
    return RkUInt8Ty(RkTy(Repr.UINT, Width.BYTE))


def uint16() -> RkUInt16Ty:
    return RkUInt16Ty(RkTy(Repr.UINT, Width.WORD))


def uint32() -> RkUInt32Ty:
    return RkUInt32Ty(RkTy(Repr.UINT, Width.DWORD))


def uint64() -> RkUInt64Ty:
    return RkUInt64Ty(RkTy(Repr.UINT, Width.QWORD))


def sint8() -> RkSInt8Ty:
    return RkSInt8Ty(RkTy(Repr.SINT, Width.BYTE))


def sint16() -> RkSInt16Ty:
    return RkSInt16Ty(RkTy(Repr.SINT, Width.WORD))


def sint32() -> RkSInt32Ty:
    return RkSInt32Ty(RkTy(Repr.SINT, Width.DWORD))


def sint64() -> RkSInt64Ty:
    return RkSInt64Ty(RkTy(Repr.SINT, Width.QWORD))


def float16() -> RkFloat16Ty:
    return RkFloat16Ty(RkTy(Repr.FLOAT, Width.WORD))


def float32() -> RkFloat32Ty:
    return RkFloat32Ty(RkTy(Repr.FLOAT, Width.DWORD))


def float64() -> RkFloat64Ty:
    return RkFloat64Ty(RkTy(Repr.FLOAT, Width.QWORD))


def bool_() -> RkBoolTy:
    return RkBoolTy(RkTy(Repr.BOOL, Width.BIT))


def string() -> RkStringTy:
    return RkStringTy(RkTy(Repr.STRING, Width.VARIABLE))


def is_uint8(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkUInt8Ty]:
    return ty.repr_ == Repr.UINT and ty.width == Width.BYTE


def is_uint16(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkUInt16Ty]:
    return ty.repr_ == Repr.UINT and ty.width == Width.WORD


def is_uint32(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkUInt32Ty]:
    return ty.repr_ == Repr.UINT and ty.width == Width.DWORD


def is_uint64(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkUInt64Ty]:
    return ty.repr_ == Repr.UINT and ty.width == Width.QWORD


def is_uint(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkUIntTy]:
    return ty.repr_ == Repr.UINT


def is_sint8(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkSInt8Ty]:
    return ty.repr_ == Repr.SINT and ty.width == Width.BYTE


def is_sint16(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkSInt16Ty]:
    return ty.repr_ == Repr.SINT and ty.width == Width.WORD


def is_sint32(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkSInt32Ty]:
    return ty.repr_ == Repr.SINT and ty.width == Width.DWORD


def is_sint64(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkSInt64Ty]:
    return ty.repr_ == Repr.SINT and ty.width == Width.QWORD


def is_sint(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkSIntTy]:
    return ty.repr_ == Repr.SINT


def is_int(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkIntTy]:
    return ty.repr_ == Repr.SINT or ty.repr_ == Repr.UINT


def is_float16(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkFloat16Ty]:
    return ty.repr_ == Repr.FLOAT and ty.width == Width.WORD


def is_float32(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkFloat32Ty]:
    return ty.repr_ == Repr.FLOAT and ty.width == Width.DWORD


def is_float64(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkFloat64Ty]:
    return ty.repr_ == Repr.FLOAT and ty.width == Width.QWORD


def is_float(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkFloatTy]:
    return ty.repr_ == Repr.FLOAT


def is_number(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkNumberTy]:
    return ty.repr_ in {Repr.UINT, Repr.SINT, Repr.FLOAT}


def is_bool(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkBoolTy]:
    return ty.repr_ == Repr.BOOL


def is_string(ty: RkTy[_Repr, _Width]) -> TypeGuard[RkStringTy]:
    return ty.repr_ == Repr.STRING
