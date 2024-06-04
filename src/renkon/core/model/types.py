"""
Base type aliases/definitions for the Renkon project.

These definitions are collected here so that:
  - They can be easily imported and used across the project,
  - They can be easily changed in one place if needed.

They are not intended to be imported outside of this project,
despite usage in public facing type hints. This may change.
"""

from typing import Annotated

from annotated_types import MinLen
from polars import PolarsDataType

# region Column Types

type ColumnName = str
type ColumnNames = tuple[ColumnName, ...]

type ColumnType = PolarsDataType
type ColumnTypes = tuple[ColumnType, ...]
type ColumnTypeSet = frozenset[ColumnType]

# endregion

# region Annotated Types

type NonEmptyList[T] = Annotated[list[T], MinLen(1)]

# endregion
