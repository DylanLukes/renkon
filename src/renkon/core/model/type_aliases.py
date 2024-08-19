from __future__ import annotations

from renkon.core.model.type import Type

type ColumnName = str
type ColumnNames = tuple[ColumnName, ...]

type ColumnType = Type
type ColumnTypes = tuple[ColumnType, ...]
type ColumnTypeSet = frozenset[ColumnType]
