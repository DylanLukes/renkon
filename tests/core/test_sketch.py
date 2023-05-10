from renkon.core import rkty
from renkon.core.sketch import Linear


def test_sketch_linear() -> None:
    for n in range(1, 3):
        sk = Linear(n)
        assert sk.arity == n + 1
        assert len(sk.holes) == n + 1

        for i in range(0, n + 1):
            assert sk.holes[i].name == f"a_{i}"
            assert sk.holes[i].py_value() is None
            assert sk.holes[i].type_ == rkty.float64()
