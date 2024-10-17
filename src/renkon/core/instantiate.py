# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from renkon.core.schema import Schema
from renkon.core.trait import ConcreteTraitSpec, MonoTraitSpec, TraitSketch, TraitSpec


def monomorphize(_base_spec: TraitSpec, _schema: Schema) -> list[MonoTraitSpec]:
    pass


def concretize(_mono_spec: MonoTraitSpec, _schema: Schema) -> list[ConcreteTraitSpec]:
    pass


def sketch_all(_base_spec: TraitSpec, _schema: Schema) -> list[TraitSketch]:
    """
    Finds all valid instantiations of a given BaseSpecTrait class for the types columns in the given schema.
    """
    return []


# def instantiate_sketch(sketch: TraitSketch) -> Trait:
#     module_name, cls_name = sketch.spec.id.rsplit(sep=".", maxsplit=1)
#
#     module = importlib.import_module(module_name)
#     trait_cls = getattr(module, cls_name)
#
#     trait_cls.instantiate(sketch.spec.)
