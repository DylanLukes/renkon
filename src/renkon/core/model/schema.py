from collections.abc import Hashable, Iterator, Mapping, Sequence
from typing import Self, overload

from polars.type_aliases import SchemaDict
from pydantic import ConfigDict, RootModel

from renkon.core.model.type import Type, tyconv_pl_to_rk
from renkon.core.model.type_aliases import ColumnName, ColumnNames


class Schema(RootModel[dict[ColumnName, Type]], Mapping[ColumnName, Type], Hashable):
    """
    Represents a schema for some or all of the columns a data frame.

    Explicitly preserves order of its entries, provides a .index method for lookup of
    the index of a column name, and convenience accessors for column names and types.

    Note that Python dict preserves insertion order since Pyt@hon 3.7.
    """

    model_config = ConfigDict(frozen=True)
    root: dict[ColumnName, Type]

    def __hash__(self) -> int:
        return hash(tuple(self.root.items()))

    @overload
    def __getitem__(self, key: ColumnName) -> Type: ...

    @overload
    def __getitem__(self, key: ColumnNames) -> Self: ...

    def __getitem__(self, key: ColumnName | ColumnNames) -> Type | Self:
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
    def dtypes(self) -> tuple[Type, ...]:
        return tuple(self.root.values())

    @classmethod
    def from_polars(cls, schema_dict: SchemaDict) -> Self:
        return cls(root={col_name: tyconv_pl_to_rk(pl_ty) for col_name, pl_ty in schema_dict.items()})

    def subschema(self, columns: Sequence[str]) -> Self:
        return self.__class__(root={col: self.root[col] for col in columns})
