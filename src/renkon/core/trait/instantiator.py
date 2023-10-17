from collections.abc import Iterable
from typing import TypeVar

from polars.datatypes import Float64, Int64, Utf8
from polars.type_aliases import SchemaDict

from renkon.core.trait.base import TraitSketch, TraitType
from renkon.core.trait.linear import Linear
from renkon.core.util.permute import permutations_with_commutativity

# TODO Unused:
# An instantiation dict maps each unique tuple of column names to a set of traits.
# TraitInstantiation = Mapping[tuple[str], set[TraitType]]

# We can't just use TraitType as the parameter type on methods like instantiate_one
# because it will produce a type error:
# "Only a concrete class can be used where 'Type[Trait]' protocol is expected"
# So instead, we use a type variable bound to TraitType which represents some
# specific concrete subclass of TraitType.
_TraitTyT = TypeVar("_TraitTyT", bound=TraitType)


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

        sketches = []

        for trait_type in trait_types:
            new_sketches = TraitSketchInstantiator.instantiate_one(trait_type, schema)
            sketches.extend(new_sketches)

        return sketches

    @staticmethod
    def instantiate_one(trait_type: _TraitTyT, schema: SchemaDict) -> list[TraitSketch]:
        """Instantiates sketches for a single trait type."""

        sketches = []

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


def test_instantiate_one() -> None:
    # Linear is commutative in all positions except the first (the dependent variable).
    trait_type = Linear
    schema: SchemaDict = {"a": Int64, "b": Float64, "c": Int64, "d": Utf8}
    sketches = TraitSketchInstantiator.instantiate_one(trait_type, schema)
    print(sketches)


def test_check_type_compatibility() -> None:
    trait_type = Linear

    schema_bad = {"a": Int64, "b": Float64, "c": Int64, "d": Utf8}
    res = TraitSketchInstantiator.check_type_compatibility(trait_type, schema_bad)
    assert res is False  # noqa: S101

    schema_ok = {"a": Int64, "b": Float64, "c": Int64}
    res = TraitSketchInstantiator.check_type_compatibility(trait_type, schema_ok)
    assert res is True  # noqa: S101
