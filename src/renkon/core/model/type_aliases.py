from __future__ import annotations

from renkon.core.model.type import RenkonType

type ColumnName = str
type ColumnNames = tuple[ColumnName, ...]

type ColumnType = RenkonType
type ColumnTypes = tuple[ColumnType, ...]
type ColumnTypeSet = frozenset[ColumnType]
