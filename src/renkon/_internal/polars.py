# Polars expr for median_absolute_deviation:

import polars as pl


@pl.api.register_expr_namespace("rk")
class RenkonPolarsUtils:
    """
    Extensions to the Polars expression namespace.
    """

    def __init__(self, expr: pl.Expr):
        self.expr = expr

    def mad(self) -> pl.Expr:
        return (self.expr - self.expr.median()).abs().median()
