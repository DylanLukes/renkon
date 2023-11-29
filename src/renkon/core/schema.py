from collections import OrderedDict
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from polars import PolarsDataType
    from polars.type_aliases import SchemaDict

type ColumnName = str
type ColumnType = PolarsDataType
type ColumnTypeSet = frozenset[ColumnType]


class Schema(Mapping[ColumnName, ColumnType]):
    """
    Represents a schema for some or all of the columns a data frame. This differs from
    a polars SchemaDict in that it explicitly preserves the order of its entries.

    Note that since Python 3.7, all dicts are ordered by insertion in any case.
    """

    _dict: OrderedDict[ColumnName, ColumnType]

    def __init__(self, schema_dict: SchemaDict, *, ordering: Sequence[ColumnName] = None):
        ordering = ordering or list(schema_dict.keys())
        self._dict = OrderedDict((col, schema_dict[col]) for col in ordering)

    @classmethod
    def from_polars(cls, schema_dict: SchemaDict) -> Self:
        return cls(schema_dict)

    def columns(self) -> Sequence[ColumnName]:
        return tuple(self._dict.keys())

    def types(self) -> Sequence[ColumnType]:
        return tuple(self._dict.values())

    def subschema(self, columns: Sequence[ColumnName]) -> Self:
        return Schema({col: self._dict[col] for col in columns})

    def __getitem__(self, column_name: ColumnName) -> ColumnType:
        return self._dict[column_name]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        schema_str = ", ".join([f"{col}: {ty}" for col, ty in self._dict])
        return f"Schema({schema_str})"
