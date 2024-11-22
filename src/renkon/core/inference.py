# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from pydantic import BaseModel

from renkon.core.schema import Schema
from renkon.core.trait import Trait, TraitSpec
from renkon.traits.linear import Linear2


class InferenceTask(BaseModel):
    """
    :ivar trait: the trait instance (!!) to infer
    :ivar schema: the schema of the input data
    :ivar bindings: mapping from metavariables to column names in the schema
    """

    trait: TraitSpec
    schema: Schema  # pyright: ignore [reportIncompatibleMethodOverride]
    bindings: dict[str, str]


class InferencePlan(BaseModel):
    tasks: list[InferenceTask]


def plan_infer_one[T: Trait](trait_type: type[T], schema: Schema) -> InferencePlan:
    raise NotImplementedError


def plan_infer_many(trait_types: list[type[Trait]], schema: Schema) -> InferencePlan:
    tasks: list[InferenceTask] = []
    for trait_type in trait_types:
        plan = plan_infer_one(trait_type, schema)
        tasks.extend(plan.tasks)
    return InferencePlan(tasks=tasks)


def test_plan_infer_one() -> None:
    trait_type = Linear2
    schema = Schema({"a": "int", "b": "float", "s": "str", "p": "bool", "c": "float"})

    _plan = plan_infer_one(trait_type, schema)
