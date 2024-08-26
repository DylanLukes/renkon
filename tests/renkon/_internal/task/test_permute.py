from renkon._internal.permute import permutations_with_commutativity


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

    assert set(observed) == set(expected)


def test_permutations_with_commutativity_preserve_order() -> None:
    a = ["c", "b", "a"]
    c = [False, True, True]

    # In all permutations, the second item should be a higher letter than the third.
    observed = list(permutations_with_commutativity(a, c, preserve_order=True))
    expected = [("c", "b", "a"), ("b", "c", "a"), ("a", "c", "b")]

    assert set(observed) == set(expected)
