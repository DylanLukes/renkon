from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Protocol, TypeAlias


@dataclass(frozen=True, slots=True)
class Kind(Protocol):
    def as_py(self) -> type:
        ...


@dataclass(frozen=True, slots=True)
class UIntKind(Kind):
    def as_py(self) -> type:
        return int


@dataclass(frozen=True, slots=True)
class IntKind(Kind):
    def as_py(self) -> type:
        return int


@dataclass(frozen=True, slots=True)
class FloatKind(Kind):
    def as_py(self) -> type:
        return float


@dataclass(frozen=True, slots=True)
class BoolKind(Kind):
    def as_py(self) -> type:
        return bool


@dataclass(frozen=True, slots=True)
class StringKind(Kind):
    def as_py(self) -> type:
        return str


AnyRepr: TypeAlias = UIntKind | IntKind | FloatKind | BoolKind | StringKind

int_ = IntKind()
uint = UIntKind()
float_ = FloatKind()
bool_ = BoolKind()
string = StringKind()
