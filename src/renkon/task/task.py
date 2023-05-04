from collections.abc import Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

_RT = TypeVar("_RT")


@dataclass
class Task(Generic[_RT]):
    """
    Generic task class, with a name and a function to run.
    """

    name: str
    func: Callable[..., _RT]


# class TypeInferTask(Task):
#     def __init__(self, name: str, func: Callable[..., _RT]):
#         super().__init__(name, func)
#
#     def __call__(self, *args, **kwargs):
#         return self.func(*args, **kwargs)
