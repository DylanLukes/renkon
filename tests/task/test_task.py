from renkon.task.task import Task


def test_task() -> None:
    task = Task("test", lambda: 42)
    assert task.name == "test"
    assert task.func() == 42
