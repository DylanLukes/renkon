import numpy as np
import polars as pl
from pytest import approx

from renkon.stats.normal import NormalModel


def test_normal_first_hundred() -> None:
    x = np.arange(0.0, 100.0)
    df = pl.DataFrame({"x": x})

    model = NormalModel("x")
    results = model.fit(df)

    assert results.params.mean == approx(np.mean(x))
    assert results.params.std == approx(np.std(x, ddof=1))  # ddof=1 for sample std
    assert results.score(df) == approx(1)


# todo: test on normal data
# todo: test on non-normal data
