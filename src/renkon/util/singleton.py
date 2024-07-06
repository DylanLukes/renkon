# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import functools
from abc import ABCMeta, abstractmethod
from types import MethodType
from typing import Any, Callable, reveal_type, Concatenate


class _SingletonMeta(ABCMeta):
    _instances: dict[type, Any] = {}

    def __call__(cls, *args: Any, **kwargs: Any):
        if cls not in cls._instances:
            cls._instances[cls] = super(_SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(metaclass=_SingletonMeta):
    @classmethod
    def get_instance(cls: type[Singleton]) -> Singleton:
        return cls()


class singletonmethod[T: Singleton, ** P, R]:
    """Descriptor for a method which when called on the class, delegates to the singleton instance."""

    func: Callable[P, R]

    def __init__(self, func: Callable[P, R], *, cls: type[T] = Singleton):
        if not callable(func) and not hasattr(func, "__get__"):
            raise TypeError(f"{func!r} is not callable or a descriptor")

        self.func = func
        functools.update_wrapper(self, func)

    def __get__(self, obj: T | None, cls: type[T]) -> MethodType:
        if obj is None:
            obj = cls.get_instance()
        return MethodType(self.func, obj)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self.func(*args, **kwargs)

    @property
    def __isabstractmethod__(self):
        return getattr(self.func, '__isabstractmethod__', False)


def fsingletonmethod[S: Singleton, ** P, R](func: Callable[Concatenate[S, P], R]) -> Callable[Concatenate[S, P], R]:
    """Decorator for a method which when called on the class, delegates to the singleton instance."""

    @functools.wraps(func)
    def wrapper(self: S, *args: P.args, **kwargs: P.kwargs) -> R:
        return func(self, *args, **kwargs)

    return wrapper


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
