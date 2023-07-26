import numpy as np
import polars as pl
import polars.testing
from pytest import approx

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

    predicted = results.predict(df[["x"]])
    expected = df["y"]

    pl.testing.assert_series_equal(predicted, expected)
