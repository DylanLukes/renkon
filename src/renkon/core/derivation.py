# """
# Derived columns are columns that are derived from other columns, but exist only within
# Renkon. This allows for inference over values derived from columns that are not present
# in the input table.
#
# For example, if the input table has columns `x` and `y`, it may be desirable to infer a
# trait such as `x ≥ median(y)`.
# """
# from collections.abc import Callable
# from functools import partial
# from typing import Generic, Protocol, TypeVar
#
# import polars as pl
# from polars import Series
# from polars.type_aliases import PythonLiteral
#
#
# class Derivation(Protocol):
#     name: str
#
#     def derive_name(self, column_name: str) -> str:
#         """
#         Produce a name for the derived column based on the name of the input column.
#         """
#         return f"{self.name}({column_name})"
#
#     def derive_values(self, column_values: Series) -> Series:
#         """
#         Produce an expression for the derived column based on the name of the input column.
#
#         In the case that the derived column is a constant, the result will contain that constant
#         repeated for each row in the input column.
#         """
#         ...
#
#
# _T = TypeVar("_T", bound=PythonLiteral)
#
#
# class Next(Derivation):
#     """
#     The Next derivation maps each element of the column to its successor.
#     """
#
#     name = "next"
#
#     def derive_values(self, column_values: Series) -> Series:
#         return column_values.shift(-1)
#
#
# class AggregateFunction(Derivation, Generic[_T]):
#     """
#     An aggregate derivation is a derivation that can be computed using an aggregate function
#     over the input column. This class exists mostly to cut down on boilerplate.
#     """
#
#     name: str
#     aggregate_fn: Callable[[Series], _T]
#
#     def derive_name(self, column_name: str) -> str:
#         return f"{self.name}({column_name})"
#
#     def derive_values(self, column_values: Series) -> Series:
#         return pl.repeat(value=self.aggregate_fn(column_values), n=column_values.len(), eager=True)
#
#
# class Mean(AggregateFunction[float]):
#     name = "mean"
#     aggregate_fn = partial(pl.mean)
#
#
# class Median(AggregateFunction[float]):
#     name = "median"
#     aggregate_fn = partial(pl.median)
