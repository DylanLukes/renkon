# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from string import Formatter
from typing import Any, Literal

from pydantic import BaseModel, field_validator, model_validator

type TemplateExtraPolicy = Literal["allow", "forbid"]


class TraitForm(BaseModel):
    """
    Model representing the form of a trait, can be templated with actual values.

    >>> TraitForm.model_validate_json('''{
    ...     "template": "{y} = {a}*{x} + {b}",
    ...     "metavars": ["x", "y"],
    ...     "params": ["a", "b"]
    ... }''')
    TraitForm(template='{y} = {a}*{x} + {b}', metavars=['x', 'y'], params=['a', 'b'])

    :param template: the f-string template of the trait form, e.g. "{y} = {a}*{x} + {b}".
    :param metavars: the names of the metavariables substituted by column names in the trait form, e.g. ["x", "y"].
    :param params: the names of the parameters to be inferred in the trait form, e.g. ["a", "b", "c"].
    """

    template: str
    metavars: list[str]
    params: list[str]

    def format(self, extra: TemplateExtraPolicy = "forbid", **kwargs: Any):
        """
        Template the trait form with the given metavariable and parameter substitutions. Must be
        complete, i.e. all metavariables and parameters must be substituted.
        """
        if extra == "forbid" and len(extra_fields := set(kwargs.keys()) - set(self.metavars + self.params)) != 0:
            raise ExtraTemplateSubstitutionError(extra_fields)

        return self.template.format_map(kwargs)

    def format_partial(self, extra: TemplateExtraPolicy = "forbid", **kwargs: Any):
        """
        Template the trait form with the given metavariable and parameter substitutions. Can be
        incomplete, i.e. not all metavariables and parameters must be substituted, in which case
        the remaining fields are left as template fields.
        """
        if extra == "forbid" and len(extra_fields := set(kwargs.keys()) - set(self.metavars + self.params)) != 0:
            raise ExtraTemplateSubstitutionError(extra_fields)

        return self.template.format_map({k: kwargs.get(k, "{" + k + "}") for k in self.metavars + self.params})

    @field_validator("metavars")
    @classmethod
    def check_unique_metavars(cls, metavars: str):
        if len(duplicate_metavars := {v for v in metavars if metavars.count(v) > 1}) > 0:
            raise DuplicateMetavarsError(duplicate_metavars)
        return metavars

    @field_validator("params")
    @classmethod
    def check_unique_params(cls, params: str):
        if len(duplicate_params := {p for p in params if params.count(p) > 1}) > 0:
            raise DuplicateParamsError(duplicate_params)
        return params

    @field_validator("template")
    @classmethod
    def check_unique_template_fields(cls, template: str):
        fields = [field_name for (_, field_name, _, _) in Formatter().parse(template) if field_name]
        if len(duplicate_template_fields := {v for v in fields if fields.count(v) > 1}) > 0:
            raise DuplicateTemplateFieldError(duplicate_template_fields)
        return template

    @model_validator(mode="after")
    def check_template(self):
        for _literal_text, field_name, _format_spec, _conversion in Formatter().parse(self.template):
            if field_name is None:  # None means only literal text, not a field
                continue
            if field_name == "":  # Empty string means anonymous field
                raise AnonymousTemplateFieldError
            if field_name not in self.metavars + self.params:
                raise UnknownTemplateFieldError(field_name)

        return self


class TraitFormValidationError(Exception): ...


class DuplicateMetavarsError(TraitFormValidationError):
    def __init__(self, duplicate_metavars: set[str]):
        super().__init__(f"Duplicate metavariables: {duplicate_metavars}", duplicate_metavars)
        self.duplicate_metavars = duplicate_metavars


class DuplicateParamsError(TraitFormValidationError):
    def __init__(self, duplicate_params: set[str]):
        super().__init__(f"Duplicate parameters: {duplicate_params}", duplicate_params)
        self.duplicate_params = duplicate_params


class AnonymousTemplateFieldError(TraitFormValidationError):
    def __init__(self):
        super().__init__("Anonymous template fields are not allowed.")


class DuplicateTemplateFieldError(TraitFormValidationError):
    def __init__(self, duplicate_template_fields: set[str]):
        super().__init__(f"Duplicate template fields: {duplicate_template_fields}", duplicate_template_fields)
        self.duplicate_template_fields = duplicate_template_fields


class UnknownTemplateFieldError(TraitFormValidationError):
    def __init__(self, field_name: str):
        super().__init__(f"Unknown template field name: {field_name}")
        self.field_name = field_name


class ExtraTemplateSubstitutionError(RuntimeError):
    def __init__(self, extra_fields: set[str]):
        super().__init__(f"Extra template substitutions: {extra_fields}", extra_fields)
        self.extra_fields = extra_fields


class MissingTemplateSubstitutionError(RuntimeError):
    def __init__(self, missing_fields: set[str]):
        super().__init__(f"Missing template substitutions: {missing_fields}", missing_fields)
        self.missing_fields = missing_fields
