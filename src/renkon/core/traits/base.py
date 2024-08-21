# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import ClassVar, Protocol, final

from renkon.core.model import TraitId, TraitKind, TraitPattern, TraitSketch, TraitSpec
from renkon.core.model.type import Type
import renkon.core.model.type as rk_type


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

    @property
    def commutors(self) -> list[set[str]]:
        return self.spec.commutors

    @property
    def typevars(self) -> dict[str, Type]:
        return self.spec.typevars

    @property
    def typings(self) -> dict[str, Type | str]:
        return self.spec.typings

    def sketch(self, **kwargs: Type) -> TraitSketch:
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
            "X": rk_type.numeric(),
            "Y": rk_type.numeric(),
            "a": rk_type.float_(),
            "b": rk_type.float_(),
        },
    )
