# def test_cereal_calories_linear(cereals_df: pl.DataFrame):
#     """
#     Test that inference is able to infer a linear model for calories:
#     calories ~ 4 x carbs + 4 x protein + 9 x fat + 4 x fiber + 4 x sugars
#
#     In actuality, the data is not exactly linear, it is off from the expected
#     value by +/- ~15 calories at most (except an outlier at 70 due to missing data)
#     and usually +/- ~5 calories.
#     """
#     pass
#
#
# def test_cereal_positive(cereals_df: pl.DataFrame):
#     """
#     Test that inference identifies that all features ought to be positive,
#     though there are some negative values in the data (representing unknowns?).
#     """
#     pass
