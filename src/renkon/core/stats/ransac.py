from dataclasses import dataclass

import numpy as np
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
    _max_trials: int
    _min_inlier_ratio: float
    _min_score: float
    _stop_inliers_pct: float
    _stop_score: float

    # Used during fit
    _n_trials: int = 0

    def __init__(
        self,
        base_model: Model[P],
        *,
        min_sample: int = 2,
        max_trials: int = 100,
        stop_inliers_pct: float = np.inf,
        stop_score: float = np.inf,
    ):
        self._base_model = base_model
        self._max_trials = max_trials
        self._stop_inliers_pct = stop_inliers_pct
        self._stop_score = stop_score
        self._stop_confidence = stop_confidence

    @property
    def y_col(self) -> str:
        return self._base_model.y_col

    @property
    def x_cols(self) -> list[str]:
        return self._base_model.x_cols

    def fit(self, data: pl.DataFrame) -> ModelResults[P]:
        data = data.with_row_count("ransac_row_nr")

        self._n_trials = 0
        while self._n_trials < self._max_trials:
            self._n_trials += 1

            # Create a binary mask series with 0s everywhere and 1st in min_sample positions.
            raise NotImplementedError()

    def predict_expr(self, params: P) -> pl.Expr:
        return self._base_model.predict_expr(params)

    def errors_expr(self, params: P, *, pred_col: str | None = None) -> pl.Expr:
        return self._base_model.errors_expr(params, pred_col=pred_col)

    def score_expr(self, params: P, *, err_col: str | None = None) -> pl.Expr:
        # todo: this should probably be different for RANSAC,
        #       i.e. modulated by the inlier ratio!
        return self._base_model.score_expr(params, err_col=err_col)
