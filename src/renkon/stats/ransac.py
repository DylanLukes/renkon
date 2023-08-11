from dataclasses import dataclass
from typing import TypeVar

import polars as pl

from renkon.stats.model import Model, Results

_ParamsT = TypeVar("_ParamsT", bound="Params")


@dataclass(kw_only=True)
class RANSACModel(Model[_ParamsT]):
    base_model: Model[_ParamsT]

    @property
    def x_cols(self) -> list[str]:
        return self.base_model.x_cols

    @property
    def y_col(self) -> str | None:
        return self.base_model.y_col

    def fit(self: Model[_ParamsT], data: pl.DataFrame) -> Results[_ParamsT]:
        pass
