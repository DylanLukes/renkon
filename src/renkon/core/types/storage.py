from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol, TypeAlias


@dataclass(frozen=True, slots=True)
class Storage(Protocol):
    def bit_width(self) -> int | None:
        ...


@dataclass(frozen=True, slots=True)
class BitStorage(Storage):
    def bit_width(self) -> int | None:
        return 1


@dataclass(frozen=True, slots=True)
class ByteStorage(Storage):
    def bit_width(self) -> int | None:
        return 8


@dataclass(frozen=True, slots=True)
class WordStorage(Storage):
    def bit_width(self) -> int | None:
        return 16


@dataclass(frozen=True, slots=True)
class DWordStorage(Storage):
    def bit_width(self) -> int | None:
        return 32


@dataclass(frozen=True, slots=True)
class QWordStorage(Storage):
    def bit_width(self) -> int | None:
        return 64


@dataclass(frozen=True, slots=True)
class VariableStorage(Storage):
    def bit_width(self) -> int | None:
        return None


AnyStorage: TypeAlias = BitStorage | ByteStorage | WordStorage | DWordStorage | QWordStorage | VariableStorage


bit = BitStorage()
byte = ByteStorage()
word = WordStorage()
dword = DWordStorage()
qword = QWordStorage()
variable = VariableStorage()
