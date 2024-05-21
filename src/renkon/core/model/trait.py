from enum import StrEnum
from typing import NewType

from pydantic import BaseModel

TraitId = NewType("TraitId", str)


class TraitSort(StrEnum):
    """
    Enum representing the possible sorts of a trait.

    The sort of a trait is a high-level categorization of the trait's nature,
    and strongly implies the process by which it is inferred and scored.

    :cvar ALGEBRAIC: An algebraic (numeric) expression over columns, e.g. "a*x + b = c".
    :cvar LOGICAL: A logical (boolean) expression over columns, e.g. "a > b".
    :cvar MODEL: A model of the data, e.g. a linear regression model.
    :cvar STATISTICAL: A statistical test or measure, e.g. a t-test.
    :cvar TEXTUAL: A textual (string) expression over columns, e.g. "a contains 'b'".

    """

    ALGEBRAIC = "algebraic"
    LOGICAL = "logical"
    MODEL = "model"
    STATISTICAL = "statistical"
    TEXTUAL = "textual"


class TraitInfo(BaseModel):
    """
    Model representing the descriptive identity of a trait.

    This is as opposed to the behavioral functionality (e.g. inference, scoring)
    found in :class:`~renkon.core.trait.Trait`.

    :param id: the unique identifier of the trait.
    :param name: the name of the trait.
    :param sort: the sort of the trait, e.g. "algebraic", "model", etc.
    :param form: the form of the trait with metavariables, e.g. "a*x + b = c"
    """

    id_: TraitId
    name: str
    sort: TraitSort
    form: str
