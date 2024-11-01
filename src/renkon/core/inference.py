# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from pydantic.dataclasses import dataclass

from renkon.core.schema import Schema
from renkon.core.trait import Trait


@dataclass
class InferenceTask:
    """
    :ivar trait: the trait to infer
    :ivar schema: the schema of the input data
    :ivar bindings: mapping from metavariables to column names in the schema
    """

    trait: Trait
    schema: Schema
    bindings: dict[str, str]


@dataclass
class InferencePlan:
    tasks: list[InferenceTask]


def plan_infer_many(trait_types: list[type[Trait]], schema: Schema) -> InferencePlan:
    tasks = []
    for trait_type in trait_types:
        plan = plan_infer_one(trait_type, schema)
        tasks.append(plan.tasks)
    return InferencePlan(tasks)


def plan_infer_one(trait_type: type[Trait], schema: Schema) -> InferencePlan:
    raise NotImplementedError
