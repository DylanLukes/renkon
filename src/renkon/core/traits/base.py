# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from abc import abstractmethod
from typing import Protocol, final

from renkon.core.model import TraitId, TraitKind, TraitPattern, TraitSpec


class TraitMeta(type[Protocol]):
    @abstractmethod
    def infer(self):
        pass


class Trait(Protocol, metaclass=TraitMeta):
    @property
    @abstractmethod
    def spec(self) -> TraitSpec: ...

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
    def metavariables(self) -> set[str]:
        return set(self.pattern.metavariables)

    @property
    def parameters(self) -> set[str]:
        return set(self.pattern.parameters)


@final
class Linear2(Trait):
    info = TraitSpec(
        id="Linear2",
        name="Linear Regression",
        kind=TraitKind.MODEL,
        pattern=TraitPattern("{y} = {a}*{x} + {b}"),
        typings={
            "x": {"numeric"},
            "y": {"numeric"},
            "a": {"float"},
            "b": {"float"},
        },
    )


if __name__ == "__main__":
    print(Linear2.info)  # noqa
