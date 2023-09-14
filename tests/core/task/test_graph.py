from typing import NoReturn, TypeVar

import pytest

from renkon.core.task.graph import TaskGraph
from renkon.core.task.result import Err, Ok, Unk

_T = TypeVar("_T")


def mk_foo() -> str:
    return "foo"


def mk_bar() -> str:
    return "bar"


def mk_baz() -> str:
    return "baz"


def mk_qux() -> str:
    return "qux"


def fail(_: _T) -> NoReturn:
    msg = "fail"
    raise RuntimeError(msg)


def test_add_task() -> None:
    g: TaskGraph[str] = TaskGraph()
    id_a = g.add_task("a", mk_foo, [])

    assert g.get_task(id_a).name == "a"
    assert g.get_task(id_a).func() == "foo"


def test_add_tasks() -> None:
    g: TaskGraph[str] = TaskGraph()

    g.add_tasks(
        [
            ("a", mk_foo, []),
            ("b", mk_bar, []),
        ]
    )


def test_no_duplicate_task_names() -> None:
    g: TaskGraph[str] = TaskGraph()
    g.add_task("a", mk_foo, [])

    with pytest.raises(ValueError):
        g.add_task("a", mk_bar, [])


def test_run_line() -> None:
    g: TaskGraph[str] = TaskGraph()

    g.add_tasks(
        [
            ("a", mk_foo, []),
            ("b", mk_bar, ["a"]),
            ("c", mk_baz, ["b"]),
        ]
    )

    g.run()

    assert g.get_result(g.task_name_to_id["a"]) == Ok("foo")
    assert g.get_result(g.task_name_to_id["b"]) == Ok("bar")
    assert g.get_result(g.task_name_to_id["c"]) == Ok("baz")


def test_run_diamond() -> None:
    g: TaskGraph[str] = TaskGraph()

    g.add_tasks(
        [
            ("a", mk_foo, []),
            ("b", mk_bar, ["a"]),
            ("c", mk_baz, ["a"]),
            ("d", mk_qux, ["b", "c"]),
        ]
    )

    g.run()

    assert g.get_result(g.task_name_to_id["a"]) == Ok("foo")
    assert g.get_result(g.task_name_to_id["b"]) == Ok("bar")
    assert g.get_result(g.task_name_to_id["c"]) == Ok("baz")
    assert g.get_result(g.task_name_to_id["d"]) == Ok("qux")


def test_run_prune_line() -> None:
    g: TaskGraph[str] = TaskGraph()

    g.add_tasks(
        [
            ("a", mk_foo, []),
            ("b", fail, ["a"]),
            ("c", mk_bar, ["b"]),
        ]
    )

    g.run()

    assert type(g.get_result(g.task_name_to_id["a"])) is Ok
    assert type(g.get_result(g.task_name_to_id["b"])) is Err
    assert type(g.get_result(g.task_name_to_id["c"])) is Unk


def test_run_prune_complex() -> None:
    g: TaskGraph[str] = TaskGraph()

    g.add_tasks(
        [
            ("a", mk_foo, []),
            ("b", mk_bar, ["a"]),
            ("c", mk_foo, []),
            ("d", mk_foo, ["b", "c"]),
            ("e", fail, ["d"]),
            ("f", mk_foo, ["e"]),
            ("g", mk_foo, ["a", "f"]),
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
