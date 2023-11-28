from collections.abc import Iterable, Sequence

from polars.datatypes import Float64, Int64, Utf8
from polars.type_aliases import SchemaDict

from renkon.core.trait.base import Trait, TraitSketch, TraitType
from renkon.core.trait.linear import Linear
from renkon.core.util.permute import permutations_with_commutativity


class TraitSketchInstantiator:
    """
    Responsible for instantiating sketches of traits for a given set of traits
    and a given set of column names and types.
    """

    @staticmethod
    def instantiate(trait_types: Iterable[TraitType], schema: SchemaDict) -> list[TraitSketch]:
        """
        Given a set of traits and a schema, instantiate the traits.
        """

        sketches: list[TraitSketch] = []

        for trait_type in trait_types:
            new_sketches = TraitSketchInstantiator.instantiate_one(trait_type, schema)
            sketches.extend(new_sketches)

        return sketches

    @staticmethod
    def instantiate_one[T: Trait](trait_type: type[T], schema: SchemaDict) -> Sequence[TraitSketch]:
        """Instantiates sketches for a single trait type."""

        sketches: list[TraitSketch] = []

        for arity in sorted(trait_type.arities()):
            col_names = tuple(schema.keys())
            commutors = trait_type.commutors(arity)
            col_perms = permutations_with_commutativity(col_names, commutors, length=arity)
            for col_perm in col_perms:
                # Take the subset of the schema that corresponds to the current permutation.
                subschema = {col_name: schema[col_name] for col_name in col_perm}
                if not TraitSketchInstantiator.check_type_compatibility(trait_type, subschema):
                    continue
                sketch = trait_type.sketch(col_perm)
                sketches.append(sketch)

        return sketches

    @staticmethod
    def check_type_compatibility(trait_type: TraitType, schema: SchemaDict) -> bool:
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
