# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from string import Formatter
from typing import TYPE_CHECKING, Any, Literal, LiteralString, NamedTuple

import pytest
from pydantic import GetCoreSchemaHandler, TypeAdapter
from pydantic_core import core_schema as cs

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator


class FStringFieldSpec(NamedTuple):
    literal_text: str | LiteralString
    field_name: str | LiteralString | None
    format_spec: str | LiteralString | None
    conversion: str | LiteralString | None


def is_valid_format_string(value: str) -> bool:
    try:
        Formatter().parse(value)
    except ValueError:
        return False
    return True


def iter_field_specs(value: str, predicate: Callable[[FStringFieldSpec], bool] = lambda _: True) -> Iterator[
    FStringFieldSpec]:
    for field_spec in Formatter().parse(value):
        field_spec = FStringFieldSpec(*field_spec)
        if predicate(field_spec):
            yield field_spec


def is_metavariable_name(s: str) -> bool:
    return s[0].isupper()


def is_parameter_name(s: str) -> bool:
    return s[0].islower()


class TraitPattern(str):
    """
    A string that represents a format string for a trait.
    None
    """
    __slots__ = (
        "parameters",
        "metavariables"
    )

    def __new__(cls, value: str):
        obj = super().__new__(cls, value)
        obj.metavariables = []
        obj.parameters = []

        if not is_valid_format_string(value):
            msg = "format string '{value}' must be a valid f-string."
            raise ValueError(msg)

        seen = set()
        for (_, field_name, _, _) in iter_field_specs(value):
            if not field_name:
                msg = "format string fields must be named."
                raise ValueError(msg)

            if field_name in seen:
                msg = f"format string field '{field_name}' must be unique."
                raise ValueError(msg)
            seen.add(field_name)

            if is_metavariable_name(field_name):
                obj.metavariables.append(field_name)
            elif is_parameter_name(field_name):
                obj.parameters.append(field_name)
            else:
                msg = f"format string field '{field_name}' must start with a letter."
                raise ValueError(msg)

        return obj

    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler
    ) -> cs.CoreSchema:
        return cs.chain_schema([
            cs.str_schema(),
            cs.no_info_plain_validator_function(lambda s: cls(s)),
        ])

    def format(
            self,
            extra: Literal["ignore", "forbid"] = "forbid",
            missing: Literal["partial", "forbid"] = "forbid",
            **mapping: Any
    ) -> str:
        if extra == "forbid":
            extra_fields = set(mapping.keys()) - set(self.metavariables + self.parameters)
            if extra_fields:
                msg = f"extra fields are forbidden: {extra_fields}."
                raise ValueError(msg)

        if missing == "forbid":
            missing_fields = set(self.metavariables + self.parameters) - set(mapping.keys())
            if missing_fields:
                msg = f"missing fields are forbidden: {missing_fields}."
                raise ValueError(msg)

        if missing == "partial":
            mapping = {k: mapping.get(k, "{" + k + "}") for k in self.metavariables + self.parameters}

        return self.format_map(mapping)


def test_trait_pattern_validation():
    ta = TypeAdapter(TraitPattern)
    pattern = ta.validate_python("{Y} = {a}*{X} + {b}")
    assert pattern.metavariables == ["Y", "X"]  # noqa: S101
    assert pattern.parameters == ["a", "b"]  # noqa: S101

    with pytest.raises(ValueError, match="must be named"):
        ta.validate_python("{} = {a}*{X} + {b")

    with pytest.raises(ValueError, match="must start with a letter"):
        ta.validate_python("{123} = {a}*{X} + b")

    with pytest.raises(ValueError, match="must be unique"):
        ta.validate_python("{Y} = {a}*{Y} + b")


def test_trait_pattern_format():
    ta = TypeAdapter(TraitPattern)
    pattern = ta.validate_python("{Y} = {a}*{X} + {b}")

    # happy case
    assert pattern.format(Y="money", X="time", a=3, b=4) == "money = 3*time + 4"

    # extra fields are forbidden when extra="forbid"
    with pytest.raises(ValueError, match="extra fields are forbidden: {'c'}."):
        pattern.format(Y="money", X="time", a=3, b=4, c=5)

    # missing fields are forbidden when missing="forbid"
    with pytest.raises(ValueError, match="missing fields are forbidden: {'b'}"):
        pattern.format(Y="money", X="time", a=3)

    # missing fields left as template fields when missing="partial"
    assert pattern.format(Y="money", a=3, missing="partial") == "money = 3*{X} + {b}"



