from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar

import pyarrow as pa
from pyarrow import lib as palib

from renkon.core.types import kind, storage
from renkon.core.types.kind import Kind, UIntKind
from renkon.core.types.storage import Storage

_K = TypeVar("_K", bound=Kind, covariant=True)
_S = TypeVar("_S", bound=Storage, covariant=True)


@dataclass(frozen=True, slots=True)
class Type(Generic[_K, _S]):
    kind: _K
    storage: _S

    def to_py(self) -> type:
        return self.kind.as_py()

    @staticmethod
    def from_py(py_type: type) -> Type[Kind, Storage] | None:
        match py_type:
            case _ if py_type is int:
                return Type(kind.int_, storage.qword)
            case _ if py_type is float:
                return Type(kind.float_, storage.qword)
            case _ if py_type is str:
                return Type(kind.string, storage.variable)
            case _ if py_type is bool:
                return Type(kind.bool_, storage.bit)
        return None

    def to_arrow(self) -> pa.DataType:
        match self.kind, self.storage:
            case kind.uint, storage.byte:
                return pa.uint8()
            case kind.uint, storage.word:
                return pa.uint16()
            case kind.uint, storage.dword:
                return pa.uint32()
            case kind.uint, storage.qword:
                return pa.uint64()
            case kind.int_, storage.byte:
                return pa.int8()
            case kind.int_, storage.word:
                return pa.int16()
            case kind.int_, storage.dword:
                return pa.int32()
            case kind.int_, storage.qword:
                return pa.int64()
            case kind.float_, storage.byte | storage.word:
                return pa.float16()
            case kind.float_, storage.dword:
                return pa.float32()
            case kind.float_, storage.qword:
                return pa.float64()
            case kind.bool_, storage.bit:
                return pa.bool_()
            case kind.string, storage.variable:
                return pa.string()
            case _:
                raise NotImplementedError()

    @staticmethod
    def from_arrow(arrow_type: pa.DataType) -> Type[Kind, Storage] | None:
        match arrow_type.id:
            case palib.Type_UINT8:
                return Type(kind.uint, storage.byte)
            case palib.Type_UINT16:
                return Type(kind.uint, storage.word)
            case palib.Type_UINT32:
                return Type(kind.uint, storage.dword)
            case palib.Type_UINT64:
                return Type(kind.uint, storage.qword)
            case palib.Type_INT8:
                return Type(kind.int_, storage.byte)
            case palib.Type_INT16:
                return Type(kind.int_, storage.word)
            case palib.Type_INT32:
                return Type(kind.int_, storage.dword)
            case palib.Type_INT64:
                return Type(kind.int_, storage.qword)
            case palib.Type_HALF_FLOAT:
                return Type(kind.float_, storage.word)
            case palib.Type_FLOAT:
                return Type(kind.float_, storage.dword)
            case palib.Type_DOUBLE:
                return Type(kind.float_, storage.qword)
            case palib.Type_BOOL:
                return Type(kind.bool_, storage.bit)
            case palib.Type_STRING:
                return Type(kind.string, storage.variable)
            case _:
                raise NotImplementedError()

    def __str__(self) -> str:
        match self.kind:
            case kind.uint | kind.int_ | kind.float_:
                return f"{self.kind}({self.storage.bit_width()})"
            case kind.string:
                return "string"
            case kind.bool_:
                return "bool"


AnyType: TypeAlias = Type[Kind, Storage]

UInt: TypeAlias = Type[UIntKind, Storage]
Int: TypeAlias = Type[kind.IntKind, Storage]
Float: TypeAlias = Type[kind.FloatKind, Storage]
Bool: TypeAlias = Type[kind.BoolKind, Storage]
String: TypeAlias = Type[kind.StringKind, Storage]

uint8 = Type(kind.uint, storage.byte)
uint16 = Type(kind.uint, storage.word)
uint32 = Type(kind.uint, storage.dword)
uint64 = Type(kind.uint, storage.qword)
int8 = Type(kind.int_, storage.byte)
int16 = Type(kind.int_, storage.word)
int32 = Type(kind.int_, storage.dword)
int64 = Type(kind.int_, storage.qword)
float16 = Type(kind.float_, storage.word)
float32 = Type(kind.float_, storage.dword)
float64 = Type(kind.float_, storage.qword)
bool_ = Type(kind.bool_, storage.bit)
string = Type(kind.string, storage.variable)
