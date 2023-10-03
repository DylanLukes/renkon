from dataclasses import dataclass


class RenkonError(Exception):
    """Base class for all Renkon errors."""

    pass


class TraitLoaderError(RenkonError):
    """Base class for all trait loader errors."""

    pass


@dataclass
class TraitNotFoundError(TraitLoaderError):
    """Raised when a trait cannot be found."""

    trait_name: str

    def __str__(self) -> str:
        return f"Trait {self.trait_name} not found."


@dataclass
class NotATraitError(TraitLoaderError):
    """Raised when a trait is invalid."""

    trait_name: str

    def __str__(self) -> str:
        return f"Class {self.trait_name} is not a trait."
