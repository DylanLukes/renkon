from collections import OrderedDict
from collections.abc import Sequence
from typing import Self

from polars import Schema as PolarsSchema
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema as cs

from renkon.core.type import RenkonType, tyconv_pl_to_rk, tyconv_rk_to_pl

BaseSchema = OrderedDict[str, RenkonType]


class Schema(BaseSchema):
    @property
    def names(self) -> list[str]:
        return list(self.keys())

    @property
    def types(self) -> list[RenkonType]:
        return list(self.values())

    def subschema(self, columns: Sequence[str]) -> Self:
        return self.__class__({col: self[col] for col in columns})

    @classmethod
    def from_polars(cls, schema: PolarsSchema):
        return cls({col: tyconv_pl_to_rk(pl_ty) for col, pl_ty in schema.items()})

    def to_polars(self) -> PolarsSchema:
        return PolarsSchema({col: tyconv_rk_to_pl(rk_ty) for col, rk_ty in self.items()})

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler, /):
        return cs.chain_schema([handler(dict), cs.no_info_plain_validator_function(cls.__call__)])
