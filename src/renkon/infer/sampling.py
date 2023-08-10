from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import polars as pl

_rng = np.random.default_rng()


class Sampler(Protocol):
    """
    A sampler is used to sample a subset of the data.

    The sampler methods return (possibly lazy) expressions that can be
    used with polars. Using expressions allows polars to optimize more.
    """

    @property
    @abstractmethod
    def indices(self) -> pl.Expr:
        """

        Usage example::

            sample = rk.sample.const(k=10)

            df.select(pl.col("...").take(sample.indices()))
        :return: an expression leading to a series of integers in the range [0, n).
        """
        ...

    @property
    @abstractmethod
    def mask(self) -> pl.Expr:
        """

        Usage example::

            sample = rk.sample.const(k=10)
            df.select(pl.col("...").filter(sample.mask()))

        Or, shorthand for all columns::

            df.filter(sampler.mask())

        :return: an expression leading to a series of booleans of length n.
        """
        ...


class _MaskFromIndicesMixin(Sampler, Protocol):
    """Default implementation of mask() in terms of indices()."""

    @property
    def mask(self) -> pl.Expr:
        row_nrs = pl.int_range(0, pl.count())
        return pl.when(row_nrs.is_in(self.indices)).then(True).otherwise(False)


@dataclass(kw_only=True)
class FullSampler(Sampler):
    """Samples all data."""

    @property
    def indices(self) -> pl.Expr:
        return pl.int_range(0, pl.count())

    @property
    def mask(self) -> pl.Expr:
        return pl.lit(True)


@dataclass(kw_only=True)
class NullSampler(Sampler):
    """Samples no data."""

    @property
    def indices(self) -> pl.Expr:
        return pl.lit([])

    @property
    def mask(self) -> pl.Expr:
        return pl.lit(False)


@dataclass(kw_only=True)
class ConstSampler(_MaskFromIndicesMixin, Sampler):
    """Samples a constant k-subset of the data."""

    k: int

    @property
    def indices(self) -> pl.Expr:
        def choose(n: int) -> pl.Series:
            # _rng.choice is constant time in n.
            return pl.Series(_rng.choice(n, self.k, replace=False))

        return pl.count().apply(choose).explode().alias("")


@dataclass(kw_only=True)
class SliceSampler(_MaskFromIndicesMixin, Sampler):
    """Samples a specific slice of the data. Useful for testing!"""

    offset: int
    length: int

    @property
    def indices(self) -> pl.Expr:
        return pl.int_range(self.offset, self.offset + self.length)


@dataclass(kw_only=True)
class FractionSampler(_MaskFromIndicesMixin, Sampler):
    """Samples a fraction f of the data."""

    f: float

    @property
    def indices(self) -> pl.Expr:
        return pl.int_range(0, pl.count()).sample(fraction=self.f)


full = FullSampler
null = NullSampler
const = ConstSampler
slice_ = SliceSampler
frac = FractionSampler
