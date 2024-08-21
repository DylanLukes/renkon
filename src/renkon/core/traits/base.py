# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import ClassVar, Protocol, final

from renkon.core.model import TraitId, TraitKind, TraitPattern, TraitSketch, TraitSpec
from renkon.core.model.type import Type, rk_float, rk_numeric


class Trait(Protocol):
    spec: ClassVar[TraitSpec]

    @property
    def id(self) -> TraitId:
        return self.spec.id

    @property
    def name(self) -> str:
        return self.spec.name

    @property
    def kind(self) -> TraitKind:
        return self.spec.kind

    @property
    def pattern(self) -> TraitPattern:
        return self.spec.pattern

    @property
    def metavars(self) -> set[str]:
        return set(self.pattern.metavars)

    @property
    def params(self) -> set[str]:
        return set(self.pattern.params)

    def sketch(self, **kwargs: dict[str, Type]) -> TraitSketch:
        return TraitSketch.model_validate(
            {
                "trait": self.spec,
                "metavar_bindings": kwargs,
            }
        )


@final
class Linear2(Trait):
    spec = TraitSpec(
        id="Linear2",
        name="Linear Regression",
        kind=TraitKind.MODEL,
        pattern=TraitPattern("{Y} = {a}*{X} + {b}"),
        typings={
            "X": rk_numeric,
            "Y": rk_numeric,
            "a": rk_float,
            "b": rk_float,
        },
    )
