from typing import Protocol


class Inference(Protocol):
    """
    An Inference represents a single inference of a given property
    over a given tuple of columns.
    """
