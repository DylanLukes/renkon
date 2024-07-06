# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from types import MethodType
from typing import Any, Callable, reveal_type, Self, ClassVar
from functools import singledispatchmethod

class _SingletonMeta(ABCMeta):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any):
        reveal_type(cls)
        if cls not in cls._instances:
            cls._instances[cls] = super(_SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=_SingletonMeta):
    __singleton__: ClassVar[Self | None] = None
    ...


class singletonmethod[T: Singleton, ** P, R]:
    """Descriptor for a method which when called on the class, delegates to the singleton instance."""

    def __init__(self, func: Callable[P, R]):
        self.func = func

    def __get__(self, obj: T | None, cls: type[T]) -> MethodType:
        if obj is None:
            obj = type(cls).__call__(cls)
        return MethodType(self.func, obj)

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, '__isabstractmethod__', False)


# Example

class Base(metaclass=ABCMeta):
    """Defines a method that must be available on subclass instances."""

    @abstractmethod
    def foo(self) -> str:
        ...


class DerivedNormal(Base):
    """Normal implementation."""

    def foo(self):
        return "normal"


class DerivedSingleton(Base, Singleton):
    """Implementation where annotation also makes foo callable from the class."""

    @singletonmethod
    def foo(self):
        return "singleton"


if __name__ == "__main__":
    reveal_type(DerivedSingleton.foo)
    reveal_type(DerivedSingleton().foo)

    assert DerivedSingleton() is DerivedSingleton()
    print(DerivedSingleton().foo())
    print(DerivedSingleton.foo())
