from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from typing import Any, Self

from polars import NUMERIC_DTYPES, DataFrame

from renkon.core.schema import ColumnTypeSet
from renkon.core.trait import TraitSketch
from renkon.core.trait.base import BaseTrait, TraitMeta


class Linear(BaseTrait[Self], ABC):
    class Meta(TraitMeta[Self]):
        _arity: int

        def __init__(self, arity: int):
            self._arity = arity

        @property
        def arity(self) -> int:
            return self._arity

        @property
        def commutors(self) -> Sequence[bool]:
            # return (False,) + (self.arity - 1) * (True,)
            return (True,) * self.arity

        @property
        def supported_dtypes(self) -> Sequence[ColumnTypeSet]:
            return (NUMERIC_DTYPES,) * self.arity

    def __init_subclass__(cls, *, arity: int, **kwargs: Any):
        cls.meta = Linear.Meta(arity=arity)
        super().__init_subclass__(**kwargs)

    @classmethod
    def infer(cls, sketch: TraitSketch[Self], data: DataFrame) -> Self:
        raise NotImplementedError


class Linear2(Linear, arity=2):
    pass


class Linear3(Linear, arity=3):
    pass


class Linear4(Linear, arity=4):
    pass
