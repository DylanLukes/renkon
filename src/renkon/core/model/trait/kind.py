# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from enum import StrEnum


class TraitKind(StrEnum):
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
