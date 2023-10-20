from dataclasses import dataclass

import polars as pl

from renkon.core.stats.base import Model, ModelParams, ModelResults


@dataclass(frozen=True, kw_only=True, slots=True)
class RANSACModelResults[P: ModelParams](ModelResults[P]):
    @property
    def model(self) -> Model[P]:
        raise NotImplementedError

    @property
    def params(self) -> P:
        raise NotImplementedError

    def score(self, params: P | None = None) -> pl.Expr:
        raise NotImplementedError


class RANSACModel[P: ModelParams](Model[P]):
    _base_model: Model[P]
    _max_iterations: int
    _min_inlier_ratio: float
    _min_score: float

    def __init__(
        self,
        base_model: Model[P],
        *,
        max_iterations: int = 100,
        min_inlier_ratio: float = 0.9,
        min_confidence: float = 0.9,
    ):
        self._base_model = base_model
        self._max_iterations = max_iterations
        self._min_inlier_ratio = min_inlier_ratio
        self._min_score = min_confidence

    @property
    def y_col(self) -> str:
        return self._base_model.y_col

    @property
    def x_cols(self) -> list[str]:
        return self._base_model.x_cols

    def fit(self, data: pl.DataFrame) -> ModelResults[P]:
        raise NotImplementedError

    def predict_expr(self, params: P) -> pl.Expr:
        return self._base_model.predict_expr(params)

    def errors_expr(self, params: P, *, pred_col: str | None = None) -> pl.Expr:
        return self._base_model.errors_expr(params, pred_col=pred_col)

    def score_expr(self, params: P, *, err_col: str | None = None) -> pl.Expr:
        # todo: this should probably be different for RANSAC,
        #       i.e. modulated by the inlier ratio!
        return self._base_model.score_expr(params, err_col=err_col)
