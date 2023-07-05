# import polars as pl
#
# from renkon.core.derivation import Mean, Median
#
#
# def test_mean() -> None:
#     deriv = Mean()
#     assert deriv.derive_name("foo") == "mean(foo)"
#     assert deriv.derive_values(pl.Series([1, 2, 3, 4])).to_list() == [2.5] * 4
#
#
# def test_median() -> None:
#     deriv = Median()
#     assert deriv.derive_name("foo") == "median(foo)"
#     assert deriv.derive_values(pl.Series([1, 2, 3, 4])).to_list() == [2.5] * 4
