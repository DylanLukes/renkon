from __future__ import annotations

from collections.abc import Generator
from typing import Any, Protocol


class Params(Protocol):
    """
    Base class for (learned) parameters of a model.

    Currently, this just needs to be unpackable. Implementations can
    expose more functionality (like named fields), but this is the bare minimum.
    """

    def __iter__(self) -> Generator[float, None, None]:
        ...
