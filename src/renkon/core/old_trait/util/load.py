import importlib
from typing import TypeGuard

from renkon.core.old_trait import AnyTrait, Trait
from renkon.errors import NotATraitError, TraitNotFoundError


def _is_trait_type(cls: type | None) -> TypeGuard[type[AnyTrait]]:
    """
    :return: whether the given class is a trait.
    """
    return cls is not None and isinstance(cls, Trait)


class TraitLoader:
    """
    Utility class for loading traits.
    """

    @staticmethod
    def load(trait_name: str) -> type[AnyTrait]:
        package_name, class_name = trait_name.rsplit(".", 1)

        try:
            module = importlib.import_module(package_name)
            klass: type = getattr(module, class_name)

            if _is_trait_type(klass):
                return klass

            raise NotATraitError(trait_name)
        except ImportError as err:
            raise TraitNotFoundError(trait_name) from err
        except AttributeError as err:
            raise TraitNotFoundError(trait_name) from err
