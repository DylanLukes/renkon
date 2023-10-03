import importlib
from typing import TypeGuard

from renkon.core.trait.base import Trait
from renkon.errors import NotATraitError, TraitNotFoundError


def is_trait_type(cls: type | None) -> TypeGuard[type[Trait]]:
    """
    :return: whether the given class is a trait.
    """
    return cls is not None and issubclass(cls, Trait)


class TraitLoader:
    """
    Utility class for loading traits.
    """

    def load(self, trait_name: str) -> type[Trait]:
        package_name, class_name = trait_name.rsplit(".", 1)
        klass: type[Trait] | None = None

        try:
            module = importlib.import_module(package_name)
            klass = getattr(module, class_name)
        except ImportError as err:
            raise TraitNotFoundError(trait_name) from err
        except AttributeError as err:
            raise TraitNotFoundError(trait_name) from err

        if not is_trait_type(klass):
            raise NotATraitError(trait_name)

        return klass
