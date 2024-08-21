# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest
from pydantic import TypeAdapter

from renkon.core.model import TraitPattern, TraitSpec, Type


def test_trait_pattern_validation_errors():
    ta = TypeAdapter(TraitPattern)
    pattern = ta.validate_python("{Y} = {a}*{X} + {b}")
    assert pattern.metavars == ["Y", "X"]
    assert pattern.params == ["a", "b"]

    with pytest.raises(ValueError, match="must be named"):
        ta.validate_python("{} = {a}*{X} + {b}")

    with pytest.raises(ValueError, match="must start with a letter"):
        ta.validate_python("{123} = {a}*{X} + b")

    with pytest.raises(ValueError, match="must be unique"):
        ta.validate_python("{Y} = {a}*{Y} + b")


def test_trait_pattern_format():
    ta = TypeAdapter(TraitPattern)
    pattern = ta.validate_python("{Y} = {a}*{X} + {b}")

    # happy case
    assert pattern.format(Y="money", X="time", a=3, b=4) == "money = 3*time + 4"

    # positional arguments are forbidden
    with pytest.raises(ValueError, match="does not accept positional arguments"):
        pattern.format("money", "time", 3, 4)

    # extra fields are forbidden when extra="forbid"
    with pytest.raises(ValueError, match="extra fields are forbidden: {'c'}"):
        pattern.format(Y="money", X="time", a=3, b=4, c=5)

    # missing fields are forbidden when missing="forbid"
    with pytest.raises(ValueError, match="missing fields are forbidden: {'b'}"):
        pattern.format(Y="money", X="time", a=3)

    # missing fields left as template fields when missing="partial"
    assert pattern.format(Y="money", a=3, missing="partial") == "money = 3*{X} + {b}"


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
    assert isinstance(trait_spec.typings["X"], Type)
    assert isinstance(trait_spec.typings["Y"], Type)
    assert isinstance(trait_spec.typings["a"], Type)
    assert isinstance(trait_spec.typings["b"], Type)


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
    assert isinstance(trait_spec.typevars["T"], Type)
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
    assert isinstance(trait_spec.typevars["T"], Type)
    assert isinstance(trait_spec.typings["X"], str)
    assert isinstance(trait_spec.typings["Y"], str)
