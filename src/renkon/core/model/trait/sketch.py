# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import Self

from pydantic import BaseModel, model_validator

import renkon.core.model.type as rk
from renkon.core.model.schema import Schema
from renkon.core.model.trait.spec import TraitSpec
from renkon.core.model.type import RenkonType


class TraitSketch(BaseModel):
    """
    Sketches out a unit of inference work

    :ivar spec: the trait being sketched.
    :ivar bindings: bindings (metavariables -> input column names)
    :ivar schema: schema (input column names -> types)
    """

    spec: TraitSpec
    bindings: dict[str, str]
    schema: Schema  # pyright: ignore [reportIncompatibleMethodOverride]


    # Inverted lookup from column name to metavariable
    _bindings_inv: dict[str, str] = {}

    # Instantiations of typevars to concrete types
    _typevar_insts: dict[str, RenkonType] = {}

    @model_validator(mode="after")
    def _populate_bindings_inv(self) -> Self:
        self._bindings_inv = {v: k for (k, v) in self.bindings.items()}
        return self

    @model_validator(mode="after")
    def _check_bindings_keys(self) -> Self:
        pattern_mvars = set(self.spec.pattern.metavars)
        bound_mvars = set(self.bindings.keys())

        missing_mvars = pattern_mvars - bound_mvars
        extra_mvars = bound_mvars - pattern_mvars

        if len(missing_mvars) > 0:
            msg = f"Metavariables {missing_mvars} are missing in bindings {self.bindings}"
            raise ValueError(msg)

        if len(extra_mvars) > 0:
            msg = f"Metavariables {extra_mvars} do not occur in pattern {self.spec.pattern}"
            raise ValueError(msg)

        return self

    @model_validator(mode="after")
    def _check_bindings_values(self) -> Self:
        for mvar, col in self.bindings.items():
            if col not in self.schema.columns:
                msg = f"Cannot bind '{mvar}' to '{col} not found in {list(self.schema.columns)}"
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _populate_typevar_insts(self) -> Self:
        """(Try to) instantiate each type variable to a concrete type."""

        col_to_type = self.schema
        mvar_to_col = self.bindings
        mvar_to_typing = self.spec.typings
        mvar_to_type = {mvar: col_to_type[col] for (mvar, col) in mvar_to_col.items()}

        typevars = self.spec.typevars
        typevar_insts: dict[str, RenkonType] = self._typevar_insts

        for typevar_name, typevar_bound in typevars.items():
            # Filter mvar_to_type to only entries that reference this type variable.
            typevar_mvar_to_type = {
                mvar: mvar_to_type[mvar]
                for (mvar, mvar_typing) in mvar_to_typing.items()
                if isinstance(mvar_typing, str) and mvar_typing == typevar_name
            }

            # Check that all the bounds are satisfied.
            for mvar, mvar_type in typevar_mvar_to_type.items():
                if not mvar_type.is_subtype(typevar_bound):
                    msg = (
                        f"Column '{mvar_to_col[mvar]} has incompatible type '{mvar_type}', "
                        f"does not satisfy bound '{typevar_bound}' of typevar '{typevar_name}'."
                    )
                    raise TypeError(msg)

            # Attempt to find a least upper bound to instantiate the typevar to.
            lub_ty = rk.union(rk.any_())
            for mvar_type in typevar_mvar_to_type.values():
                lub_ty &= rk.union(mvar_type)
            lub_ty = lub_ty.normalize()

            if lub_ty == rk.none():
                msg = f"Could not instantiate typevar '{typevar_name}' given concrete typings {typevar_mvar_to_type}"
                raise TypeError(msg)

            typevar_insts[typevar_name] = lub_ty

        self._typevar_insts = typevar_insts
        return self

    @model_validator(mode="after")
    def _check_bindings_typings(self) -> Self:
        for col, ty in self.schema.items():
            mvar = self._bindings_inv[col]
            req_ty = self.spec.typings[mvar]

            if isinstance(req_ty, str):
                req_ty = self._typevar_insts[req_ty]

            if not ty.is_subtype(req_ty):
                msg = f"Column '{col}' has incompatible type '{ty}', does not satisfy bound '{req_ty}'."
                raise TypeError(msg)

        return self
