from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True, slots=True)
class Task(Generic[_T]):
    """
    Generic task class, with a name and a function to run.
    """

    name: str
    func: Callable[..., _T]
