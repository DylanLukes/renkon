from __future__ import annotations

from typing import NoReturn, TypeVar


def unreachable() -> NoReturn:  # pragma: no cover
    msg = "unreachable"
    raise AssertionError(msg)


T = TypeVar("T")
