from renkon.task.result import Err, Ok, Unk


def test_result_ok() -> None:
    ok = Ok(42)
    assert ok.value == 42
    assert repr(ok) == "Ok(42)"


def test_result_err() -> None:
    err = Err(ValueError("oops"))
    assert err.cause.args == ("oops",)
    assert repr(err) == "Err(ValueError('oops'))"


def test_result_unk() -> None:
    unk = Unk()
    assert repr(unk) == "Unk"
