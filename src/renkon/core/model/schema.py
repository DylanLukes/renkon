import sys
from collections.abc import Sequence
from typing import Self

from polars.type_aliases import SchemaDict as PolarsSchemaDict
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema as cs

from renkon.core.model.type import RenkonType, tyconv_pl_to_rk, tyconv_rk_to_pl

type ColumnName = str
type ColumnNames = tuple[ColumnName, ...]

type ColumnType = RenkonType
type ColumnTypes = tuple[ColumnType, ...]
type ColumnTypeSet = frozenset[ColumnType]

if sys.version_info <= (3, 6):
    raise RuntimeError("Dictionaries are not guaranteed to preserve order before Python 3.6.")


class Schema(dict[str, RenkonType]):
    @property
    def columns(self):
        return list(self.keys())

    @property
    def types(self):
        return list(self.values())

    def subschema(self, columns: Sequence[str]) -> Self:
        return self.__class__({col: self[col] for col in columns})

    @classmethod
    def from_polars(cls, schema: PolarsSchemaDict):
        return cls({col: tyconv_pl_to_rk(pl_ty) for col, pl_ty in schema.items()})

    def to_polars(self) -> PolarsSchemaDict:
        return {col: tyconv_rk_to_pl(rk_ty) for col, rk_ty in self.items()}

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler, /):
        return cs.chain_schema([handler(dict), cs.no_info_plain_validator_function(cls.__call__)])
