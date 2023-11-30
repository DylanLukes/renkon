__all__ = [
    "Trait",
    "TraitSketch",
    "TraitMeta",
    "BaseTrait",
    "Linear",
    "Linear2",
    "Linear3",
    "Linear4",
    "EqualNumeric",
    "EqualString",
]

from renkon.core.trait.base import BaseTrait, Trait, TraitMeta, TraitSketch
from renkon.core.trait.equal import EqualNumeric, EqualString
from renkon.core.trait.linear import Linear, Linear2, Linear3, Linear4
