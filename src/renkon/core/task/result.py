from dataclasses import dataclass
from typing import Generic, TypeVar

_T = TypeVar("_T")


@dataclass(frozen=True, slots=True)
class Ok(Generic[_T]):
    """
    Represents a successful result, carrying the value.
    """

    value: _T

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclass(frozen=True, slots=True)
class Err:
    """
    Represents an error result, carrying the responsible exception.
    """

    cause: BaseException

    def __repr__(self) -> str:
        return f"Err({self.cause!r})"


class Unk:
    """
    Represents an unknown (not yet computed?) result.
    """

    def __repr__(self) -> str:
        return "Unk"


type Result[_T] = Ok[_T] | Err | Unk
