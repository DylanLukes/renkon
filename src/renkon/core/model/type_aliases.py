from __future__ import annotations

from typing import Any

type RenkonDataType = Any  # TODO: fix

type ColumnName = str
type ColumnNames = tuple[ColumnName, ...]

type ColumnType = RenkonDataType
type ColumnTypes = tuple[ColumnType, ...]
type ColumnTypeSet = frozenset[ColumnType]
