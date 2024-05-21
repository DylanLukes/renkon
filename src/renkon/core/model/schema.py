from collections import OrderedDict
from collections.abc import Hashable, Iterator, Mapping, Sequence
from typing import Self, overload

from polars.type_aliases import SchemaDict
from pydantic import ConfigDict, RootModel

from renkon.core.model.type_aliases import ColumnName, ColumnNames, ColumnType, ColumnTypes


class Schema(RootModel[OrderedDict[ColumnName, ColumnType]], Mapping[ColumnName, ColumnType], Hashable):
    """
    Represents a schema for some or all of the columns a data frame.

    Explicitly preserves order of its entries, provides a .index method for lookup of
    the index of a column name, and convenience accessors for column names and types.
    """

    model_config = ConfigDict(frozen=True)
    root: OrderedDict[ColumnName, ColumnType]

    def __hash__(self) -> int:
        return hash(tuple(self.root.items()))

    @overload
    def __getitem__(self, key: ColumnName) -> ColumnType: ...

    @overload
    def __getitem__(self, key: ColumnNames) -> Self: ...

    def __getitem__(self, key: ColumnName | ColumnNames) -> ColumnType | Self:
        match key:
            case str():
                return self.root[key]
            case tuple():
                return self.subschema(key)

    def __iter__(self) -> Iterator[ColumnName]:  # type: ignore
        yield from iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def __lt__(self, other: Self) -> bool:
        """Compares two schemas by their column names in lexicographic order."""
        return self.columns < other.columns

    @property
    def columns(self) -> ColumnNames:
        return tuple(self.root.keys())

    @property
    def dtypes(self) -> ColumnTypes:
        return tuple(self.root.values())

    @classmethod
    def from_polars(cls, schema_dict: SchemaDict) -> Self:
        return cls(root=OrderedDict(schema_dict))

    def to_polars(self) -> SchemaDict:
        return self.root

    def subschema(self, columns: Sequence[str]) -> Self:
        return self.__class__(root=OrderedDict({col: self.root[col] for col in columns}))


# class _OldSchema(Mapping[str, PolarsDataType]):
#     """
#     Represents a schema for some or all of the columns a data frame. This differs from
#     a polars SchemaDict in that it explicitly preserves the order of its entries.
#
#     Unlike OrderedDict, this class provides an .index method for lookup of the index of a column name.
#     """
#
#     _dict: OrderedDict[str, ColumnType]
#     _order: tuple[str, ...]
#
#     def __init__(self, schema_dict: SchemaDict, *, ordering: Sequence[str] | None = None):
#         """
#         @param schema_dict: A mapping of column names to column types.
#         @param ordering: The order in which the columns should be stored. If not provided, the order
#                          will be the order in which the columns are iterated over in the schema_dict.
#         """
#         ordering = ordering or list(schema_dict.keys())
#         self._dict = OrderedDict((col, schema_dict[col]) for col in ordering)
#         self._order = tuple(ordering)
#
#     @property
#     def columns(self) -> tuple[str, ...]:
#         return tuple(self._dict.keys())
#
#     @property
#     def dtypes(self) -> tuple[ColumnType, ...]:
#         return tuple(self._dict.values())
#
#     @classmethod
#     def from_polars(cls, schema_dict: SchemaDict) -> Self:
#         return cls(schema_dict)
#
#     def to_polars(self) -> SchemaDict:
#         return self._dict
#
#     def subschema(self, columns: Sequence[str]) -> Self:
#         return self.__class__({col: self._dict[col] for col in columns}, ordering=tuple(columns))
#
#     def index(self, column_name: str) -> int | None:
#         return self._order.index(column_name) if column_name in self._order else None
#
#     def __getitem__(self, column_name: str) -> ColumnType:
#         return self._dict[column_name]
#
#     def __iter__(self):
#         return iter(self._dict)
#
#     def __len__(self):
#         return len(self._dict)
#
#     def __lt__(self, other: Self) -> bool:
#         return self._order < other._order
#
#     def __hash__(self):
#         return hash(tuple(self._dict.items()))
#
#     def __str__(self):
#         schema_str = ", ".join([f"{col}: {ty}" for col, ty in self._dict.items()])
#         return f"{{{schema_str}}}"
