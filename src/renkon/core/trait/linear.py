from __future__ import annotations

from abc import ABC
from collections.abc import Sequence
from typing import Any, ClassVar

from polars import NUMERIC_DTYPES, DataFrame

from renkon.core.schema import ColumnTypeSet
from renkon.core.trait import TraitSketch
from renkon.core.trait.base import BaseTrait, TraitMeta


class Linear(BaseTrait["Linear"], ABC):
    class Meta(TraitMeta["Linear"]):
        _arity: int

        def __init__(self, arity: int = 2):
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

    meta: ClassVar[Linear.Meta]

    def __init_subclass__(cls, arity: int = 2, **kwargs: Any):
        super().__init_subclass__(**kwargs)

        # See: https://github.com/python/typing/discussions/1486
        cls.meta = Linear.Meta(arity=arity)  # type: ignore

    @classmethod
    def infer[T: "Linear"](cls: type[T], sketch: TraitSketch[T], data: DataFrame) -> T:
        raise NotImplementedError


class Linear2(Linear, arity=2):
    pass


class Linear3(Linear, arity=3):
    pass


class Linear4(Linear, arity=4):
    pass
