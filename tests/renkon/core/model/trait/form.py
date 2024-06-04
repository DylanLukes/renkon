# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import pytest

from renkon.core.model.trait import (
    AnonymousTemplateFieldError,
    DuplicateMetavarsError,
    DuplicateParamsError,
    DuplicateTemplateFieldError,
    TraitForm,
    UnknownTemplateFieldError,
)


def test_trait_form_round_trip() -> None:
    trait_form = expected = TraitForm(template="{y} = {a}*{x} + {b}", metavars=["x", "y"], params=["a", "b"])

    json_data = trait_form.model_dump_json()
    actual = TraitForm.model_validate_json(json_data)

    assert actual == expected


def test_trait_form_template_validation() -> None:
    with pytest.raises(DuplicateMetavarsError):
        TraitForm(template="{y} = {a}*{x} + {b}", metavars=["x", "y", "x"], params=["a", "b"])

    with pytest.raises(DuplicateParamsError):
        TraitForm(template="{y} = {a}*{x} + {b}", metavars=["x", "y"], params=["a", "b", "a"])

    with pytest.raises(AnonymousTemplateFieldError):
        TraitForm(template="{} = {a}*{x} + {b}", metavars=["x", "y"], params=["a", "b"])

    with pytest.raises(DuplicateTemplateFieldError):
        TraitForm(template="{y} = {a}*{x} + {b} + {b}", metavars=["x", "y"], params=["a", "b"])

    with pytest.raises(UnknownTemplateFieldError):
        TraitForm(template="{y} = {a}*{z} + {b}", metavars=["x", "y"], params=["a", "b"])
