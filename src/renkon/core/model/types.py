"""
Base type aliases/definitions for the Renkon project.

These definitions are collected here so that:
  - They can be easily imported and used across the project,
  - They can be easily changed in one place if needed.

They are not intended to be imported outside of this project,
despite usage in public facing type hints. This may change.
"""

# TODO: hide implementation detail of using Polars?
from polars import PolarsDataType
from polars import datatypes as pldt

# region Basic Types
type RenkonDataType = Int | Float | Decimal | String | Bool | Binary | Date | Datetime | Time

type Int = pldt.Int64
type Float = pldt.Float64
type Decimal = pldt.Decimal
type String = pldt.String
type Bool = pldt.Boolean
type Binary = pldt.Binary
type Date = pldt.Date
type Datetime = pldt.Datetime
type Time = pldt.Time
# endregion

# region Type Groups
type Numeric = Int | Float | Decimal
type Temporal = Date | Datetime | Time
type Text = String

# region Column Types
type ColumnName = str
type ColumnNames = tuple[ColumnName, ...]

type ColumnType = PolarsDataType
type ColumnTypes = tuple[ColumnType, ...]
type ColumnTypeSet = frozenset[ColumnType]
# endregion
