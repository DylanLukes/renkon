# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

import functools
from abc import ABCMeta
from collections.abc import Callable
from typing import Any, Concatenate


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


# if TYPE_CHECKING:
#     def singletonmethod[**P, R](_method: Callable[P, R]) -> Callable[P, R]:
#         ...
# else:
class singletonmethod[T: Singleton, ** P, R]:
    """Descriptor for a method which when called on the class, delegates to the singleton instance."""

    method: Callable[Concatenate[T, P], R]
    instance: T | None

    def __init__(self, method: Callable[Concatenate[T, P], R], instance: T | None = None):
        if not callable(method) and not hasattr(method, "__get__"):
            raise TypeError(f"{method!r} is not callable or a descriptor")
        self.method = method
        self.instance = instance

    def __get__(self, instance: T | None, owner: type[T]) -> Callable[P, R]:
        instance = instance or owner.get_instance()
        descriptor = self.__class__(self.method, instance)
        functools.update_wrapper(descriptor, self.method)
        return descriptor

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        if self.instance is None:
            raise TypeError("singletonmethod instance is not set")
        return self.method(self.instance, *args, **kwargs)

    @property
    def __isabstractmethod__(self):
        return getattr(self.method, '__isabstractmethod__', False)


class instancemethod[T, ** P, R]:
    method: Callable[Concatenate[T, P], R]
    instance: T | None

    def __init__(self, method: Callable[Concatenate[T, P], R], instance: T | None = None):
        self.method = method
        self.instance = instance

    def __get__(self, instance: T | None, owner: type[T]) -> Callable[P, R]:
        descriptor = self.__class__(self.method, instance)
        functools.update_wrapper(descriptor, self.method)
        return descriptor

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        if self.instance is None:
            raise TypeError("instancemethod called directly, not on instance")
        return self.method(self.instance, *args, **kwargs)


# class Base(ABC):
#     # foo: Callable[[], str]
#     def foo(self) -> str:
#         return "foo"
#
#
# class DerivedNormal(Base):
#     def _foo(self) -> str:
#         return "foo"
#     foo = instancemethod(_foo)
#
# class DerivedSingleton2(Base, Singleton):
#     @singletonmethod
#     def foo(self) -> str:
#         return "foo"
#
# class DerivedSingleton(Base, Singleton):
#     def _foo(self) -> str:
#         return "foo"
#     foo = singletonmethod(_foo)
#
#
# def test_singleton():
#     assert "foo" == DerivedNormal.foo()
#     assert "foo" == DerivedSingleton.foo() == DerivedSingleton().foo()
