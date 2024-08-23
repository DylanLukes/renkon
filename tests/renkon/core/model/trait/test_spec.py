# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from renkon.core.model import RenkonType, TraitSpec


def test_trait_spec_validate_json():
    trait1 = TraitSpec.model_validate_json("""{
        "id": "renkon.test.Linear2",
        "name": "Test Linear",
        "kind": "model",

        "pattern": "{Y} = {a}*{X} + {b}",
        "typings": {
            "X": "numeric",
            "Y": "numeric",
            "a": "float",
            "b": "float"
        }
    }""")

    assert trait1.metavars == {"Y", "X"}
    assert trait1.params == {"a", "b"}


def test_trait_spec_validate_concrete_typings():
    trait_spec = TraitSpec.model_validate(
        {
            "id": "renkon.test.Linear2",
            "name": "Test Linear",
            "kind": "model",
            "pattern": "{Y} = {a}*{X} + {b}",
            "typings": {"X": "numeric", "Y": "numeric", "a": "float", "b": "float"},
        }
    )

    assert trait_spec.metavars == {"Y", "X"}
    assert trait_spec.params == {"a", "b"}
    assert isinstance(trait_spec.typings["X"], RenkonType)
    assert isinstance(trait_spec.typings["Y"], RenkonType)
    assert isinstance(trait_spec.typings["a"], RenkonType)
    assert isinstance(trait_spec.typings["b"], RenkonType)


def test_trait_spec_validate_typevar_typings():
    trait_spec = TraitSpec.model_validate(
        {
            "id": "renkon.test.Equal",
            "name": "Test Equal",
            "kind": "logical",
            "pattern": "{X} = {Y}",
            "typevars": {
                "T": "equatable",
            },
            "typings": {
                "X": "T",
                "Y": "T",
            },
        }
    )

    assert trait_spec.metavars == {"X", "Y"}
    assert trait_spec.params == set()
    assert isinstance(trait_spec.typevars["T"], RenkonType)
    assert isinstance(trait_spec.typings["X"], str)
    assert isinstance(trait_spec.typings["Y"], str)


def test_trait_spec_validate_mixed_typings():
    trait_spec = TraitSpec.model_validate(
        {
            "id": "renkon.test.ApproxEqual",
            "name": "Test Approx Equal",
            "kind": "logical",
            "pattern": "{X} ≈ {Y} (+/- {eps})",
            "typevars": {
                "T": "numeric",
            },
            "typings": {"X": "T", "Y": "T", "eps": "float"},
        }
    )

    assert trait_spec.metavars == {"X", "Y"}
    assert trait_spec.params == {"eps"}
    assert isinstance(trait_spec.typevars["T"], RenkonType)
    assert isinstance(trait_spec.typings["X"], str)
    assert isinstance(trait_spec.typings["Y"], str)
