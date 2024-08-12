from collections.abc import Hashable, Iterator, Mapping, Sequence
from typing import Self, overload

from polars.type_aliases import SchemaDict
from pydantic import ConfigDict, RootModel

from renkon.core.model.datatypes import TypeSystem
from renkon.core.model.type_aliases import ColumnName, ColumnNames, ColumnType, ColumnTypes


class Schema(RootModel[dict[ColumnName, ColumnType]], Mapping[ColumnName, ColumnType], Hashable):
    """
    Represents a schema for some or all of the columns a data frame.

    Explicitly preserves order of its entries, provides a .index method for lookup of
    the index of a column name, and convenience accessors for column names and types.

    Note that Python dict preserves insertion order since Pyt@hon 3.7.
    """

    model_config = ConfigDict(frozen=True)
    root: dict[ColumnName, ColumnType]

    def __hash__(self) -> int:
        return hash(tuple(self.root.items()))

    @overload
    def __getitem__(self, key: ColumnName) -> ColumnType:
        ...

    @overload
    def __getitem__(self, key: ColumnNames) -> Self:
        ...

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
        return cls(root={col_name: TypeSystem.from_polars(polars_type) for col_name, polars_type in schema_dict})

    def subschema(self, columns: Sequence[str]) -> Self:
        return self.__class__(root={col: self.root[col] for col in columns})
