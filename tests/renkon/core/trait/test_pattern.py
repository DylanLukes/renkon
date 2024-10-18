# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest
from pydantic import BaseModel, TypeAdapter

from renkon.core.trait import TraitPattern


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


def test_trait_pattern_as_base_model_field():
    class Model(BaseModel):
        pattern: TraitPattern

    expected = Model.model_construct(pattern=TraitPattern("{Y} = {a}*{X} + {b}"))
    observed = Model.model_validate({"pattern": "{Y} = {a}*{X} + {b}"})
    assert expected == observed
