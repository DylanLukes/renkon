from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import polars as pl
from loguru import logger

_rng = np.random.default_rng()


class Sampler(Protocol):
    """
    A sampler is used to sample a subset of the data.

    The sampler methods return (possibly lazy) expressions that can be
    used with polars. Using expressions allows polars to optimize more.
    """

    @abstractmethod
    def indices(self) -> pl.Expr:
        """

        Usage example::

            sampler = rk.sample.const(k=10)
            df.select(pl.col("...").take(sampler.indices()))

        :return: an expression leading to a series of integers in the range [0, n).
        """
        ...

    @abstractmethod
    def mask(self) -> pl.Expr:
        """

        Usage example::

            sampler = rk.sample.const(k=10)
            df.select(pl.col("...").filter(sampler.mask()))

        Or, shorthand for all columns::

            df.filter(sampler.mask())

        :return: an expression leading to a series of booleans of length n.
        """
        ...


@dataclass(kw_only=True)
class FullSampler(Sampler):
    """Samples all data."""

    def indices(self) -> pl.Expr:
        return pl.int_range(0, pl.count())

    def mask(self) -> pl.Expr:
        return pl.lit(True)


@dataclass(kw_only=True)
class NullSampler(Sampler):
    """Samples no data."""

    def indices(self) -> pl.Expr:
        return pl.lit([])

    def mask(self) -> pl.Expr:
        return pl.lit(False)


@dataclass(kw_only=True)
class ConstSampler(Sampler):
    """Samples a constant k-subset of the data."""

    k: int

    def indices(self) -> pl.Expr:
        def choose(n):
            # _rng.choice is constant time in n.
            return pl.Series(_rng.choice(n, self.k, replace=False))

        return pl.count().apply(choose).explode().alias("")

    def mask(self) -> pl.Expr:
        row_nrs = pl.int_range(0, pl.count())
        return pl.when(row_nrs.is_in(self.indices())).then(True).otherwise(False)


@dataclass(kw_only=True)
class FractionSampler(Sampler):
    """Samples a fraction f of the data."""

    f: float

    def indices(self) -> pl.Expr:
        return pl.int_range(0, pl.count()).sample(fraction=self.f)

    def mask(self) -> pl.Expr:
        row_nrs = pl.int_range(0, pl.count())
        return pl.when(row_nrs.is_in(self.indices())).then(True).otherwise(False)


def full() -> FullSampler:
    return FullSampler()


def null() -> NullSampler:
    return NullSampler()


def const(*, k: int) -> ConstSampler:
    return ConstSampler(k=k)


def frac(*, f: float) -> FractionSampler:
    return FractionSampler(f=f)
