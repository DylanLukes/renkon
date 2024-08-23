# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
"""
Unary traits related to refining the "type" of a column beyond what is included in the
dataframe schema. For example, a column of type float might actually (almost) always consist
of just integers.

Refinements in a Renkon sense are a stronger concept than predicates, as they quantify the
conformance of the column's data. For example, _how close_ to being integral.
"""
from abc import ABC
from typing import ClassVar

from renkon.core.model.type import UnionType
from renkon.core.traits.base import Trait


class _Refinement(Trait, ABC):
    refines: ClassVar[UnionType]

    #noinspection PyMethodOverriding
    def __init_subclass__(cls, *, refines: UnionType, **kwargs: None):


class NonNull(_Refinement, refines=):
