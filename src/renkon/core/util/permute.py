"""
Custom iterable tools extensions.
"""
import itertools as it
from abc import abstractmethod
from collections.abc import Sequence
from typing import Protocol, TypeVar

_T = TypeVar("_T", bound="_Comparable")


# For some reason this isn't in the Python standard library?
class _Comparable(Protocol):
    @abstractmethod
    def __lt__(self: _T, other: _T) -> bool:
        pass


def permutations_with_commutativity(
    items: Sequence[_T], comm: Sequence[bool], *, length: int, preserve_order: bool = False
) -> list[tuple[_T, ...]]:
    """
    Generates all distinct permutations of the given items up to commutativity.

    The commutativity is specified by a sequence of booleans, where True indicates
    that the corresponding item is commutative.

    The returned permutations are _canonical_, meaning that the commutative items
    are sorted in the order they appear in the original sequence.

    @param items: an iterable of items to permute.
    @param comm: a sequence of booleans indicating whether each item is commutative.
    @param length: the length of the permutations to generate.
    @param preserve_order: if True, the commutative items will be sorted in the order
                           they appear in the original sequence. If False, they will
                           be sorted in ascending order.
    """

    # Generate iterator of all permutations. (Note that it.permutations preserves order.)
    all_perms = it.permutations(items, r=length)
    distinct_perms: set[tuple[_T, ...]] = set()

    for perm in all_perms:
        # Just the commutative items in original order.
        comm_items = tuple(perm[i] for i in range(len(perm)) if comm[i])

        # A sort key to put commutative items in canonical order.
        sort_key = (lambda x: items.index(x)) if preserve_order else None

        # Sort the commutative items into canonical order.
        comm_items_sort = tuple(sorted(comm_items, key=sort_key))

        # A mapping from each commutative item to its canonical position.
        reordering = dict(zip(comm_items, comm_items_sort))

        # Map the permutation to its canonical form.
        canon_perm = tuple(x if x not in comm_items else reordering[x] for x in perm)

        # Add the canonical permutation to the set of distinct permutations, if it's not already there.
        if canon_perm not in distinct_perms:
            distinct_perms.add(canon_perm)

    return list(distinct_perms)


def test_permutations_with_commutativity_trivial() -> None:
    """
    All positions commute, so should only have one result.
    """
    a = ["a", "b", "c", "d"]
    c = [True, True, True, True]

    observed = permutations_with_commutativity(a, c)
    expected = [("a", "b", "c", "d")]

    assert set(observed) == set(expected)


def test_permutations_with_commutativity_simple() -> None:
    """
    The result should be all permutations, minus those where the only difference
    is that y and z are swapped. In this simple case, that means only the
    position of x determines whether a permutation is distinct.
    """
    a = ["a", "b", "c"]
    c = [False, True, True]

    observed = list(permutations_with_commutativity(a, c))
    expected = [("a", "b", "c"), ("b", "a", "c"), ("c", "a", "b")]

    assert set(observed) == set(expected)  # noqa: S101


def test_permutations_with_commutativity_preserve_order() -> None:
    a = ["c", "b", "a"]
    c = [False, True, True]

    # In all permutations, the second item should be a higher letter than the third.
    observed = list(permutations_with_commutativity(a, c, preserve_order=True))
    expected = [("c", "b", "a"), ("b", "c", "a"), ("a", "c", "b")]

    assert set(observed) == set(expected)  # noqa: S101
