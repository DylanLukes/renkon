from dataclasses import dataclass
from functools import lru_cache
from typing import TypeAlias


@dataclass(frozen=True, slots=True)
class Storage:
    pass


@dataclass(frozen=True, slots=True)
class BitStorage(Storage):
    pass


@dataclass(frozen=True, slots=True)
class ByteStorage(Storage):
    pass


@dataclass(frozen=True, slots=True)
class WordStorage(Storage):
    pass


@dataclass(frozen=True, slots=True)
class DWordStorage(Storage):
    pass


@dataclass(frozen=True, slots=True)
class QWordStorage(Storage):
    pass


@dataclass(frozen=True, slots=True)
class VariableStorage(Storage):
    pass


AnyStorage: TypeAlias = BitStorage | ByteStorage | WordStorage | DWordStorage | QWordStorage | VariableStorage


bit = BitStorage()
byte = ByteStorage()
word = WordStorage()
dword = DWordStorage()
qword = QWordStorage()
variable = VariableStorage()
