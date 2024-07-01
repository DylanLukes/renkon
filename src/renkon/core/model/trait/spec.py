# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

__TRAIT_INFO__ = "__trait_info__"

from pydantic import BaseModel

from renkon.core.model.datatypes import RenkonDataType
from renkon.core.model.trait.kind import TraitKind
from renkon.core.model.trait.pattern import TraitPattern
from renkon.core.model.type_aliases import ColumnTypeSet

type TraitId = str
type TraitTypings = dict[str, RenkonDataType]


class TraitSpec(BaseModel):
    """
    Model representing the descriptive identity of a trait.

    This is as opposed to the behavioral functionality (e.g. inference, scoring)
    found in :class:`~renkon.core.trait.Trait`.

    >>> trait = TraitSpec.model_validate_json('''{
    ...     "id": "renkon.core.trait.linear.Linear2",
    ...     "name": "Linear Regression (2D)",
    ...     "kind": "model",
    ...     "pattern": "{y} = {a}*{x} + {b}",
    ...     "typings": {
    ...         "x": "numeric",
    ...         "y": "numeric",
    ...         "a": "float",
    ...         "b": "float"
    ...     }
    ... }''')

    :param id: the unique identifier of the trait.
    :param name: the human-readable name of the trait.
    :param kind: the sort of the trait, e.g. "algebraic", "model", etc.
    :param form: the human-readable form of the trait with metavariables, e.g. "y = a*x + b"
    :param metavars: the names of the metavariables substituted by column names in the trait form, e.g. ["x", "y"].
    :param params: the names of the parameters to be inferred in the trait form, e.g. ["a", "b", "c"].
    """

    id: TraitId
    name: str
    kind: TraitKind
    pattern: TraitPattern
    typings: dict[str, ColumnTypeSet]
