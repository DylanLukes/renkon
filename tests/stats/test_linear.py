import numpy as np
import polars as pl
import polars.testing
import pytest
from pytest import approx
from scipy.stats import t  # type: ignore[import]

from renkon.stats.linear import OLSModel
from renkon.util.polars import RenkonPolarsUtils  # noqa: F401


def test_linear_perfect_fit() -> None:
    x = np.arange(0.0, 1000.0)
    y = 13.0 * x + 37.0

    # Collate data, split out 10% for testing.
    df = pl.DataFrame({"x": x, "y": y})
    df, df_test = df[:900], df[900:]

    # Construct a model and fit it.
    model = OLSModel("y", ["x"], fit_intercept=True)
    fit = model.fit(df)

    # Test if the fit is correct.
    m, c = fit.params.m, fit.params.c
    assert m == approx(13)
    assert c == approx(37)

    # Test if the model properly scores the test data.
    score = df_test.select(fit.score()).item()
    assert score == approx(1.0)

    # Test if the model properly predicts the test data.
    y_pred = df_test.select(model.predict(fit.params)).get_column("y")
    pl.testing.assert_series_equal(y_pred, df_test["y"])


@pytest.mark.flaky(reruns=5, rerun_delay=1)
def test_linear_noisy_fit() -> None:
    # This is a statistical test, and rarely may fail. Reset the random seed before each test run.
    np.random.seed()
    n = 1000
    noise_std = 10.0

    x = np.arange(0.0, 1000.0)
    y = 13.0 * x + 37.0
    y_noisy = y + np.random.normal(0.0, noise_std, n)
    df = pl.DataFrame({"x": x, "y": y_noisy})
    df, df_test = df[:900], df[900:]

    model = OLSModel("y", ["x"])
    fit = model.fit(df)

    # Compute the critical value for a two-tailed t-test.
    alpha = 0.05
    dof = len(df) - 2 - 1
    t_crit = t.ppf(1 - alpha / 2, dof)

    # Get the standard errors of the slope and intercept.
    se_c, se_m = fit.bse

    # Test if the fit is correct: params within t_crit * se of the true values.
    m, c = fit.params.m, fit.params.c
    assert m == approx(13, abs=se_m * t_crit)
    assert c == approx(37, abs=se_c * t_crit)

    # Test if the model properly scores the test data.
    score = df.select(fit.score()).item()
    assert score == approx(1.0, rel=0.01)

    # Calculate the standard error of estimate (SE)
    # se_estimate = np.sqrt((results.resid**2).sum() / dof)

    # Expect predicted values to be within 3 * noise_factor of the true values.
    y_pred = df_test.select(fit.predict()).get_column("y")
    pl.testing.assert_series_equal(df_test["y"], y_pred, atol=3 * noise_std)


def test_linear_outlier_detection() -> None:
    x = np.arange(0.0, 100.0)
    y = x
    df = pl.DataFrame({"x": x, "y": y})

    model = OLSModel("y", ["x"], fit_intercept=True)
    fit = model.fit(df)

    # Produce some data that could not be explained by this model:
    bad_x = np.arange(0.0, 100.0, 10.0)
    bad_y = np.random.randint(100, 1000, len(bad_x))
    bad_df = pl.DataFrame({"x": bad_x, "y": bad_y})

    _train_mad = df.select(pl.col("y").rk.mad()).item()  # type: ignore[attr-defined]
    assert not bad_df.select((fit.errors().abs() < _train_mad).any()).item()
    assert df.select((fit.errors().abs() < _train_mad).all()).item()
