import numpy as np
import polars as pl
import polars.testing
import pytest
from pytest import approx
from scipy.stats import t

from renkon.stats.models.linear import OLSModel


def test_linear_perfect_fit() -> None:
    x = np.arange(0.0, 100.0)
    y = x
    df = pl.DataFrame({"x": x, "y": y})

    model = OLSModel("y", ["x"])
    results = model.fit(df)

    assert results.params.m == [approx(1)]
    assert results.params.c == approx(0)
    assert results.score(df) == approx(1.0)

    pl.testing.assert_series_equal(results.predict(df[["x"]]), df["y"])


@pytest.mark.flaky(reruns=5)
def test_linear_noisy_fit() -> None:
    sigma = 1.0

    x = np.arange(0.0, 100.0)
    y = x + np.random.normal(0.0, sigma, 100)
    df = pl.DataFrame({"x": x, "y": y})

    model = OLSModel("y", ["x"])
    results = model.fit(df)

    alpha = 0.05
    dof = len(df) - 2
    err_margin = t.ppf(1 - alpha / 2, dof) * sigma

    # todo: These values aren't based in any mathematical estimates.
    assert results.params.m == [approx(1, abs=err_margin)]
    assert results.params.c == approx(0, abs=err_margin)
    assert results.score(df) == approx(1.0, rel=0.1)

    # Expect predicted values to be within 3 sigma of the actual values.
    # This could fail, so this test has been marked as flaky.
    pl.testing.assert_series_equal(results.predict(df[["x"]]), df["y"], atol=4 * sigma)
