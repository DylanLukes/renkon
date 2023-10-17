import importlib
from typing import TypeGuard

from renkon.core.trait.base import Trait, TraitType
from renkon.errors import NotATraitError, TraitNotFoundError


def is_trait_type(cls: type | None) -> TypeGuard[TraitType]:
    """
    :return: whether the given class is a trait.
    """
    return cls is not None and issubclass(cls, Trait)


class TraitLoader:
    """
    Utility class for loading traits.
    """

    @staticmethod
    def load(trait_name: str) -> TraitType:
        package_name, class_name = trait_name.rsplit(".", 1)

        try:
            module = importlib.import_module(package_name)
            klass: TraitType = getattr(module, class_name)

            if not is_trait_type(klass):
                raise NotATraitError(trait_name)

            return klass
        except ImportError as err:
            raise TraitNotFoundError(trait_name) from err
        except AttributeError as err:
            raise TraitNotFoundError(trait_name) from err
