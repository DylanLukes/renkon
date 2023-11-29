from collections.abc import Iterable, Sequence

from polars.datatypes import Float64, Int64, Utf8
from polars.type_aliases import SchemaDict

from renkon.core.schema import Schema
from renkon.core.trait.base import Trait, TraitSketch, TraitType
from renkon.core.trait.linear import Linear
from renkon.core.util.permute import permutations_with_commutativity


def check_type_compatibility(trait_type: TraitType, schema: Schema) -> bool:
    arity = len(schema)
    for col_name, valid_dtypes in zip(schema.keys(), trait_type.dtypes(arity), strict=True):
        if schema[col_name] not in valid_dtypes:
            return False
    return True


class TraitSketchInstantiator:
    """
    Responsible for instantiating sketches of traits for a given set of traits
    and a given set of column names and types.
    """

    def instantiate(self, trait_types: Iterable[TraitType], schema: Schema) -> list[TraitSketch]:
        """
        Given a set of traits and a schema, instantiate sketches for the traits.
        """

        sketches: list[TraitSketch] = []

        for trait_type in trait_types:
            new_sketches = TraitSketchInstantiator.instantiate_one(trait_type, schema)
            sketches.extend(new_sketches)

        return sketches

    def instantiate_one[T: Trait](self, trait_type: type[T], schema: Schema) -> Sequence[TraitSketch]:
        """Instantiates sketches for all arities/permutations of the given schema, for a single trait type."""

        sketches: list[TraitSketch] = []

        for arity in sorted(trait_type.arities()):
            col = tuple(schema.keys())
            commutors = trait_type.commutors(arity)
            col_perms = permutations_with_commutativity(col, commutors, length=arity)
            for col_perm in col_perms:
                # Take the subset of the schema that corresponds to the current permutation.

                subschema = schema.subschema(col_perm)
                if not check_type_compatibility(trait_type, subschema):
                    continue

                sketch = TraitSketch(trait_type=trait_type, schema=subschema)
                sketches.append(sketch)

        return sketches

    @staticmethod
    def check_type_compatibility(trait_type: TraitType, schema: Schema) -> bool:
        arity = len(schema)
        for col_name, valid_dtypes in zip(schema.keys(), trait_type.dtypes(arity), strict=True):
            if schema[col_name] not in valid_dtypes:
                return False
        return True


def test_instantiate_many() -> None:
    instantiator = TraitSketchInstantiator()

    # todo: fix Normal
    trait_types = [
        Linear,
        # Normal
    ]
    schema: SchemaDict = {"a": Int64, "b": Float64, "c": Int64, "d": Utf8}
    instantiator.instantiate(trait_types, schema)


def test_instantiate_one() -> None:
    instantiator = TraitSketchInstantiator()

    # Linear is commutative in all positions except the first (the dependent variable).
    trait_type = Linear
    schema: SchemaDict = {"a": Int64, "b": Float64, "c": Int64, "d": Utf8}
    instantiator.instantiate_one(trait_type, schema)


def test_check_type_compatibility() -> None:
    instantiator = TraitSketchInstantiator()
    trait_type = Linear

    schema_bad = {"a": Int64, "b": Float64, "c": Int64, "d": Utf8}
    res = instantiator.check_type_compatibility(trait_type, schema_bad)
    assert res is False  # noqa: S101

    schema_ok = {"a": Int64, "b": Float64, "c": Int64}
    res = instantiator.check_type_compatibility(trait_type, schema_ok)
    assert res is True  # noqa: S101
