"""
Not all TypeAliases are here, just the ones that are completely ubiquitous throughout the codebase,
but don't logically belong to a particular module (e.g. TraitType in core.trait.base).

They may eventually move here.
"""

from typing import TypeAlias

ColumnName: TypeAlias = str
