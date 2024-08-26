# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from string import Formatter
from typing import TYPE_CHECKING, Annotated, Any, Literal, LiteralString, NamedTuple, TypeGuard

from annotated_types import Predicate
from pydantic_core import core_schema as cs

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from pydantic import GetCoreSchemaHandler


def is_format_string(value: str) -> bool:
    try:
        Formatter().parse(value)
    except ValueError:
        return False
    return True


def is_metavariable_name(s: str) -> TypeGuard[MetavariableName]:
    return s[0].isupper()


def is_parameter_name(s: str) -> TypeGuard[ParameterName]:
    return s[0].islower()


type FormatString = Annotated[str, Predicate(is_format_string)]
type MetavariableName = Annotated[str, Predicate(is_metavariable_name)]
type ParameterName = Annotated[str, Predicate(is_parameter_name)]


class _FStringField(NamedTuple):
    literal_text: str | LiteralString
    field_name: str | LiteralString | None
    format_spec: str | LiteralString | None
    conversion: str | LiteralString | None


def _iter_fstring_fields(value: str, pred: Callable[[_FStringField], bool] = lambda _: True) -> Iterator[_FStringField]:
    for field_tuple in Formatter().parse(value):
        field = _FStringField(*field_tuple)
        if pred(field):
            yield field


class TraitPattern(str):
    """
    A string that represents a format string for a trait.
    None
    """

    __slots__ = ("metavars", "params")

    def __new__(cls, f_str: str):
        obj = super().__new__(cls, f_str)
        obj.metavars = []
        obj.params = []

        if not is_format_string(f_str):
            msg = "format string '{value}' must be a valid f-string."
            raise ValueError(msg)

        seen: set[str] = set()
        fields = list(_iter_fstring_fields(f_str))
        for lit_text, field_name, _fmt, _cnv in fields:
            if not field_name:
                if not lit_text:
                    # This is an empty {}
                    msg = f"format string field must be named in '{f_str}'"
                    raise ValueError(msg)
                continue

            if field_name in seen:
                msg = f"format string field '{field_name}' must be unique."
                raise ValueError(msg)
            seen.add(field_name)

            if is_metavariable_name(field_name):
                obj.metavars.append(field_name)
            elif is_parameter_name(field_name):
                obj.params.append(field_name)
            else:
                msg = f"format string field '{field_name}' must start with a letter."
                raise ValueError(msg)

        return obj

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: GetCoreSchemaHandler) -> cs.CoreSchema:
        return cs.chain_schema(
            [
                cs.str_schema(),
                cs.no_info_plain_validator_function(cls),
            ]
        )

    def format(
        self,
        *args: Any,
        extra: Literal["ignore", "forbid"] = "forbid",
        missing: Literal["partial", "forbid"] = "forbid",
        **mapping: Any,
    ) -> str:
        if args:
            msg = "TraitPattern.format() does not accept positional arguments."
            raise ValueError(msg)

        if extra == "forbid":
            extra_fields = set(mapping.keys()) - set(self.metavars + self.params)
            if extra_fields:
                msg = f"extra fields are forbidden: {extra_fields}."
                raise ValueError(msg)

        if missing == "forbid":
            missing_fields = set(self.metavars + self.params) - set(mapping.keys())
            if missing_fields:
                msg = f"missing fields are forbidden: {missing_fields}."
                raise ValueError(msg)

        if missing == "partial":
            mapping = {k: mapping.get(k, "{" + k + "}") for k in self.metavars + self.params}

        return self.format_map(mapping)
