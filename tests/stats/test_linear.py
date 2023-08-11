import numpy as np
import polars as pl
import polars.testing
import pytest
from pytest import approx
from scipy.stats import t

from renkon.stats.linear import OLSModel


def test_linear_perfect_fit() -> None:
    x = np.arange(0.0, 100.0)
    y = x
    df = pl.DataFrame({"x": x, "y": y})

    model = OLSModel("y", ["x"], fit_intercept=True)
    results = model.fit(df)

    assert results.params.m == [approx(1)]
    assert results.params.c == approx(0)
    assert results.score(df) == approx(1.0)

    y_pred = df.select(model.predict(results.params)).get_column("y")

    pl.testing.assert_series_equal(y_pred, df["y"])


@pytest.mark.flaky(reruns=5, rerun_delay=1)
def test_linear_noisy_fit() -> None:
    # This is a statistical test, and rarely may fail. Reset the random seed before each test run.
    np.random.seed()

    n = 1000
    noise_factor = 1.0

    x = np.arange(0.0, n)
    y_true = x
    y_noisy = y_true + np.random.normal(0.0, noise_factor, n)
    df = pl.DataFrame({"x": x, "y": y_noisy})

    model = OLSModel("y", ["x"])
    results = model.fit(df)

    # Assert that the true parameters are within the 95% confidence interval of the estimated parameters.
    alpha = 0.05
    dof = len(df) - 2 - 1
    t_crit = t.ppf(1 - alpha / 2, dof)
    se_c, se_m = results.bse

    assert results.params.c == approx(0.0, abs=se_c * t_crit)
    assert results.params.m[0] == approx(1.0, abs=se_m * t_crit)
    assert results.score(df) == approx(1.0, rel=0.1)

    # Calculate the standard error of estimate (SE)
    se_estimate = np.sqrt((results.resid**2).sum() / dof)

    # Expect predicted values to be within 3 standard errors of estimate of the true values.
    y_pred = df.select(model.predict(results.params)).get_column("y").to_numpy()
    np.testing.assert_allclose(y_pred, y_true, atol=3 * se_estimate)


def test_linear_outlier_detection() -> None:
    x = np.arange(0.0, 100.0)
    y = x
    df = pl.DataFrame({"x": x, "y": y})

    model = OLSModel("y", ["x"], fit_intercept=True)
    results = model.fit(df)

    # Produce some data that could not be explained by this model:

    # y = 2x + 100
    df_outlier = pl.DataFrame({"x": [0.0, 1.0, 2.0, 3.0], "y": [0.0, 1.0, 2.0, 30.0]})

    expected_inliers = pl.Series("is_inlier", [True, True, True, False])
    observed_inliers = results.test_inliers(df_outlier)

    pl.testing.assert_series_equal(expected_inliers, observed_inliers)
