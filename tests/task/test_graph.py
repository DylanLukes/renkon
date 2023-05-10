from collections.abc import Callable
from typing import TypeVar

import pytest
from toolz import curry, identity

from renkon.task.graph import TaskGraph
from renkon.task.result import Err, Ok, Unk

T = TypeVar("T")


def identitwo(x: T, _: object) -> T:
    """Like identity, but with an extra argument that is ignored."""
    return x


def const(x: T) -> Callable[[object], T]:
    return curry(identitwo, x)  # type: ignore


def fail(_: T) -> T:
    msg = "fail"
    raise RuntimeError(msg)


def test_add_task() -> None:
    g: TaskGraph[int] = TaskGraph()
    id_a = g.add_task("a", curry(identity, 42), [])

    assert g.get_task(id_a).name == "a"
    assert g.get_task(id_a).func() == 42


def test_add_tasks() -> None:
    g: TaskGraph[int] = TaskGraph()

    g.add_tasks(
        [
            ("a", curry(identity, 42), []),
            ("b", curry(identity, 43), []),
        ]
    )


def test_no_duplicate_task_names() -> None:
    g: TaskGraph[int] = TaskGraph()
    g.add_task("a", curry(identity, 42), [])

    with pytest.raises(ValueError):
        g.add_task("a", curry(identity, 42), [])


def test_run_line() -> None:
    g: TaskGraph[int] = TaskGraph()

    g.add_tasks(
        [
            ("a", const(42), []),
            ("b", const(43), ["a"]),
            ("c", const(44), ["b"]),
        ]
    )

    g.run()

    assert g.get_result(g.task_name_to_id["a"]) == Ok(42)
    assert g.get_result(g.task_name_to_id["b"]) == Ok(43)
    assert g.get_result(g.task_name_to_id["c"]) == Ok(44)


def test_run_diamond() -> None:
    g: TaskGraph[int] = TaskGraph()

    g.add_tasks(
        [
            ("a", const(42), []),
            ("b", const(43), ["a"]),
            ("c", const(44), ["a"]),
            ("d", const(45), ["b", "c"]),
        ]
    )

    g.run()

    assert g.get_result(g.task_name_to_id["a"]) == Ok(42)
    assert g.get_result(g.task_name_to_id["b"]) == Ok(43)
    assert g.get_result(g.task_name_to_id["c"]) == Ok(44)
    assert g.get_result(g.task_name_to_id["d"]) == Ok(45)


def test_run_prune_line() -> None:
    g: TaskGraph[int] = TaskGraph()

    g.add_tasks(
        [
            ("a", const(42), []),
            ("b", fail, ["a"]),
            ("c", const(44), ["b"]),
        ]
    )

    g.run()

    assert type(g.get_result(g.task_name_to_id["a"])) is Ok
    assert type(g.get_result(g.task_name_to_id["b"])) is Err
    assert type(g.get_result(g.task_name_to_id["c"])) is Unk


def test_run_prune_complex() -> None:
    g: TaskGraph[int] = TaskGraph()

    g.add_tasks(
        [
            ("a", const(42), []),
            ("b", const(43), ["a"]),
            ("c", const(44), []),
            ("d", const(45), ["b", "c"]),
            ("e", fail, ["d"]),
            ("f", const(47), ["e"]),
            ("g", const(48), ["a", "f"]),
        ]
    )

    g.run()

    assert type(g.get_result(g.task_name_to_id["a"])) is Ok
    assert type(g.get_result(g.task_name_to_id["b"])) is Ok
    assert type(g.get_result(g.task_name_to_id["c"])) is Ok
    assert type(g.get_result(g.task_name_to_id["d"])) is Ok
    assert type(g.get_result(g.task_name_to_id["e"])) is Err
    assert type(g.get_result(g.task_name_to_id["f"])) is Unk
    assert type(g.get_result(g.task_name_to_id["g"])) is Unk
