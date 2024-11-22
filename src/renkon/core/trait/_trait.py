# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Protocol, Self

from pydantic import TypeAdapter

from renkon.core.trait._spec import ConcreteTraitSpec
from renkon.core.type import RenkonType

if TYPE_CHECKING:
    from polars import DataFrame

    from renkon.core.trait import TraitId, TraitKind, TraitPattern, TraitResult, TraitSpec


class Trait(Protocol):
    """
    Represents a single potential trait of a dataset pending inference.
    """

    @classmethod
    @abstractmethod
    def instantiate(cls, typevar_bindings: dict[str, RenkonType]) -> Self:
        """
        Instantiate this Trait with the given types. The resulting trait
        should always be such that :py:func:`is_monomorphized` is true.

        :param typevar_bindings: A mapping from trait typevars to Renkon types.
        :returns: a (monormophized) Trait instance.
        """
        raise NotImplementedError

    @abstractmethod
    def infer(self, data: DataFrame, column_bindings: dict[str, str]) -> TraitResult:
        """
        :param data: The data to infer from.
        :param bindings: A map from trait metavariables to data column names.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def spec(self) -> ConcreteTraitSpec:
        """
        Every Trait *instance* has a specification that describes the Trait
        almost fully, short of the inference behavior.

        In most cases, this is derived from the `base_spec` class variable of
        :class:`BaseSpecTrait`. However, Traits instances may also be created
        directly or by other means, so long as they implement this protocol.
        """
        raise NotImplementedError

    # Convenience Delegate Queries

    @property
    def id(self) -> TraitId:
        return self.spec.id

    @property
    def name(self) -> str:
        return self.spec.label

    @property
    def kind(self) -> TraitKind:
        return self.spec.kind

    @property
    def pattern(self) -> TraitPattern:
        return self.spec.pattern

    @property
    def metavars(self) -> set[str]:
        return set(self.pattern.metavars)

    @property
    def params(self) -> set[str]:
        return set(self.pattern.params)

    @property
    def commutors(self) -> set[str]:
        return self.spec.commutors

    @property
    def typevars(self) -> dict[str, RenkonType]:
        return self.spec.typevars

    @property
    def typings(self) -> dict[str, RenkonType | str]:
        return self.spec.typings

    # Validation Queries
    # ------------------

    def is_monomorphic(self) -> bool:
        """
        Check that this Trait is a monomorphized trait with only concrete types,
        and all type variables eliminated.

        :returns: True if this Trait has no polymorphic type variables.
        """
        return not self.spec.typevars and all(isinstance(ty, RenkonType) for ty in self.typings.values())


class BaseSpecTrait(Trait, ABC):
    """
    Trait defined in terms of a base TraitSpec, which is refined by
    some process during instantiation.
    """

    base_spec: ClassVar[TraitSpec]
    _inst_spec: ConcreteTraitSpec

    def __init__(self, spec: ConcreteTraitSpec):
        """
        In general, __init__ should not be called directly. It enforces several
        properties of the specification provided to it.
        """
        self._inst_spec = TypeAdapter(ConcreteTraitSpec).validate_python(spec)  # TODO: make Mono?

    @classmethod
    def instantiate(cls, typevar_bindings: dict[str, RenkonType]) -> Self:
        inst_typevars: dict[str, RenkonType] = dict(cls.base_spec.typevars)
        inst_typings: dict[str, RenkonType | str] = dict(cls.base_spec.typings)

        # Substitute the type bindings.
        for mvar, ty in inst_typings.items():
            match ty:
                case RenkonType():
                    continue
                case str():
                    inst_typings[mvar] = typevar_bindings[ty]

        # Remove the substituted type variables.
        for tv in typevar_bindings:
            if tv in typevar_bindings:
                inst_typevars.pop(tv)

        inst_typings = {
            k: ty if isinstance(ty, RenkonType) else typevar_bindings[k] for k, ty in cls.base_spec.typings.items()
        }

        inst_spec = cls.base_spec.model_copy(
            update={
                "typevars": inst_typevars,
                "typings": inst_typings,
            }
        ).as_concrete_spec()

        return cls(inst_spec)

    @property
    def spec(self) -> ConcreteTraitSpec:
        return self._inst_spec
