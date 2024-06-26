# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from abc import abstractmethod
from typing import Annotated, Protocol, final

__TRAIT_INFO__ = "__trait_info__"

from annotated_types import Gt, Lt
from pydantic import BaseModel

from renkon.core.model.trait import TraitKind
from renkon.core.model.trait.form import TraitForm

type TraitId = str
type TraitScore = Annotated[float, Gt(0.0), Lt(1.0)]


class TraitSpec(BaseModel):
    """
    Model representing the descriptive identity of a trait.

    This is as opposed to the behavioral functionality (e.g. inference, scoring)
    found in :class:`~renkon.core.trait.Trait`.

    >>> trait = TraitSpec.model_validate_json('''{
    ...     "id": "renkon.core.trait.linear.Linear2",
    ...     "name": "Linear Regression (2D)",
    ...     "sort": "model",
    ...     "form": {
    ...         "template": "{y} = {a}*{x} + {b}",
    ...         "metavars": ["y", "x"],
    ...         "params": ["a", "b"]
    ...     }
    ... }''')

    :param id: the unique identifier of the trait.
    :param name: the name of the trait.
    :param sort: the sort of the trait, e.g. "algebraic", "model", etc.
    :param form: the human-readable form of the trait with metavariables, e.g. "y = a*x + b"
    :param metavars: the names of the metavariables substituted by column names in the trait form, e.g. ["x", "y"].
    :param params: the names of the parameters to be inferred in the trait form, e.g. ["a", "b", "c"].
    """

    id: TraitId
    name: str
    sort: TraitKind
    form: TraitForm


class TraitDisplay:
    """ """


class TraitInfer:
    """ """


class Trait(Protocol):
    """
    :param R: the type of the result of the trait's inference.
    :cvar info: the metadata for this trait.
    """

    @property
    @abstractmethod
    def info(self) -> TraitSpec: ...

    @property
    @abstractmethod
    def view(self) -> TraitDisplay: ...

    @property
    @abstractmethod
    def infer(self) -> TraitInfer: ...

    @property
    def form(self) -> TraitForm:
        return self.info.form


@final
class Linear(Trait):
    pass


if __name__ == "__main__":
    print(Linear.info)  # noqa
