import functools
from abc import ABC, abstractmethod
from types import MethodType
from typing import Callable, Concatenate


class noopdecorator[T, ** P, R]:
    def __init__(self, func: Callable[P, R]):
        self.__func__ = func

    def __get__(self, obj: T | None, cls: type[T]) -> MethodType:
        return MethodType(self.__func__, obj)


def fnoopdecorator[T, ** P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


def fnoopdecorator2[T, ** P, R](func: Callable[Concatenate[T, P], R]) -> Callable[Concatenate[T, P], R]:
    @functools.wraps(func)
    def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
        return func(self, *args, **kwargs)

    return wrapper


class Base(ABC):
    @abstractmethod
    def foo(self) -> str:
        ...


class DerivedPlain(Base):
    def foo(self):
        return "simple"


class DerivedClassDecorated(Base):
    @noopdecorator
    def foo(self):
        return "decorated"


class DerivedFunctionalDecorated(Base):
    @fnoopdecorator
    def foo(self):
        return "decorated"


class DerivedFancyFunctionalDecorated(Base):
    @fnoopdecorator2
    def foo(self):
        return "decorated"
