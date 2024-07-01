from __future__ import annotations

from renkon.core.model.datatypes import DataType, DataTypeClass

type RenkonDataType = DataTypeClass | DataType

type ColumnName = str
type ColumnNames = tuple[ColumnName, ...]

type ColumnType = RenkonDataType
type ColumnTypes = tuple[ColumnType, ...]
type ColumnTypeSet = frozenset[ColumnType]
