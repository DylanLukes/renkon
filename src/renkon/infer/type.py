"""
Pandas, Arrow, and Numpy types all differ in their coverage and semantics.

Here, we overlay our own set of types on top of them, to make it easier to
work with them.
"""
from enum import Enum


class Type(Enum):
    """
    The type of a column in a DataFrame or Arrow array.
    """

    INT = 1
    FLOAT = 2
    BOOL = 3
    STRING = 4
    DATETIME = 5
    CATEGORICAL = 6
    UNKNOWN = 7
