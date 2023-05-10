from renkon.core.sketch import Linear


def test_sketch_linear() -> None:
    sk = Linear(2)
    assert sk.arity == 3
    assert len(sk.holes) == 3
    assert sk.holes[0].name == "a_0"
    assert sk.holes[0].py_value() is None
