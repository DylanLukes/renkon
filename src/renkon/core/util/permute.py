"""
Custom iterable tools extensions.
"""
import itertools as it
from collections import OrderedDict
from collections.abc import Callable, Sequence
from typing import Any, Protocol

from loguru import logger

# We need to define these protocols ourselves for everything to typecheck properly.
# For some reason the stdlib typing doesn't provide anything equivalent.
# These definitions are adapted from Typeshed's private stdlib.


class SupportsDunderLT(Protocol):
    def __lt__(self, __other: Any) -> bool:
        ...


class SupportsDunderGT(Protocol):
    def __gt__(self, __other: Any) -> bool:
        ...


type SupportsRichComparison = SupportsDunderLT | SupportsDunderGT


def permutations_with_commutativity[
    T: SupportsRichComparison,
](items: Sequence[T], comm: Sequence[bool], *, length: int | None = None, preserve_order: bool = False) -> list[
    tuple[T, ...]
]:
    """
    Generates all distinct permutations of the given items up to commutativity.

    The commutativity is specified by a sequence of booleans, where True indicates
    that the corresponding item is commutative.

    The returned permutations are _canonical_, meaning that the commutative items
    are sorted in the order they appear in the original sequence.

    @param items: an iterable of items to permute.
    @param comm: a sequence of booleans indicating whether each item is commutative.
    @param length: the length of the permutations to generate, defaults to len(items)
    @param preserve_order: if True, the commutative items will be sorted in the order
                           they appear in the original sequence. If False, they will
                           be sorted in ascending order.
    """

    if length is None:
        length = len(items)

    # Generate iterator of all permutations. (Note that it.permutations preserves order.)
    all_perms = it.permutations(items, r=length)

    # Used as an ordered set.
    distinct_perms: OrderedDict[tuple[T, ...], ()] = OrderedDict()

    # todo: all_perms is deterministically ordered but...
    for perm in all_perms:
        # Just the commutative items in original order.
        comm_items = tuple(perm[i] for i in range(len(perm)) if comm[i])

        # A sort key to put commutative items in canonical order.
        sort_key: Callable[[T], int] | None = (lambda x: items.index(x)) if preserve_order else None

        # Sort the commutative items into canonical order.
        comm_items_sort = tuple(sorted(comm_items, key=sort_key))

        # A mapping from each commutative item to its canonical position.
        reordering = dict(zip(comm_items, comm_items_sort, strict=True))

        # Map the permutation to its canonical form.
        canon_perm = tuple(x if x not in comm_items else reordering[x] for x in perm)

        # Add the canonical permutation to the set of distinct permutations, if it's not already there.
        if canon_perm not in distinct_perms:
            distinct_perms[canon_perm] = ()

    return list(distinct_perms.keys())
