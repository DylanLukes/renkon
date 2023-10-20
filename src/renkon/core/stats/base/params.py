from __future__ import annotations

from typing import Protocol


class ModelParams(Protocol):
    """
    Base class for (learned) parameters of a model.

    Doesn't really do anything. Just here for type hinting.
    """
