from collections.abc import Sequence

from renkon._internal.permute import permutations_with_commutativity
from renkon.core.model import Schema
from renkon.core.old_trait import AnyTrait, TraitMeta, TraitSketch


def check_type_compatibility(meta: TraitMeta, schema: Schema) -> bool:
    if len(schema) != meta.arity:
        return False

    for dtype, supported_dtypes in zip(schema.types, meta.supported_dtypes, strict=True):
        if dtype not in supported_dtypes:
            return False

    return True


def instantiate_trait[T: AnyTrait](trait_type: type[T], schema: Schema) -> Sequence[TraitSketch[T]]:
    """Instantiates sketches for all arities/permutations of the given schema, for a single trait type."""

    meta = trait_type.meta
    columns = schema.columns

    arity = meta.arity
    commutors = meta.commutors

    column_perms = permutations_with_commutativity(columns, commutors, length=arity)

    sketches: list[TraitSketch[T]] = []
    for column_perm in column_perms:
        # Take the subset of the schema that corresponds to the current permutation.
        subschema = schema.subschema(column_perm)

        if not check_type_compatibility(trait_type.meta, subschema):
            continue

        sketch: TraitSketch[T] = TraitSketch(trait_type=trait_type, schema=subschema)
        sketches.append(sketch)

    return sketches
