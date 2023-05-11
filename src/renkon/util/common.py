from __future__ import annotations

from typing import NoReturn


def unreachable() -> NoReturn:
    msg = "unreachable"
    raise AssertionError(msg)
