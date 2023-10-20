from dataclasses import dataclass

import polars as pl

from renkon.core.stats.base import Model, Params, Results


@dataclass(frozen=True, kw_only=True, slots=True)
class RANSACResults[P: Params](Results[P]):
    @property
    def model(self) -> Model[P]:
        raise NotImplementedError

    @property
    def params(self) -> P:
        raise NotImplementedError

    def score(self) -> pl.Expr:
        raise NotImplementedError
