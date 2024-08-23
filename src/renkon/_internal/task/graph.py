from collections import defaultdict
from collections.abc import Callable
from functools import partial
from multiprocessing import Event, Pool

from loguru import logger

from renkon._internal.task.result import Err, Ok, Result, Unk
from renkon._internal.task.task import Task
from renkon._internal.dag import DAG

type TaskSpec[T] = tuple[str, Callable[..., T], list[str]]


class TaskGraph[T]:
    """
    Implements a task graph with dependencies using python multiprocessing,
    generic in the return type of the tasks.

    The idea is that you instantiate one of these per frame of data, and it
    will run all the inference tasks in parallel, respecting dependencies.

    There is no special support for data sharing between tasks.
    """

    __slots__ = ("task_dag", "task_id_to_name", "task_id_to_result", "task_name_to_id")

    task_dag: DAG[Task[T]]

    task_id_to_name: dict[int, str]
    task_id_to_result: dict[int, Result[T]]
    task_name_to_id: dict[str, int]

    def __init__(self) -> None:
        self.task_dag = DAG[Task[T]]()
        self.task_id_to_name = {}
        self.task_id_to_result = defaultdict(Unk)
        self.task_name_to_id = {}

    def add_task(self, name: str, func: Callable[..., T], dependencies: list[int]) -> int:
        """
        Add a single task to the graph to be run after the dependencies.
        """
        if name in self.task_name_to_id:
            msg = f"Task {name} already exists!"
            raise ValueError(msg)

        # Wrap the task in a Task object.
        task = Task(name, func)
        task_id = self.task_dag.add_node(task, dependencies)

        # Store the mapping from task id to name (and back).
        self.task_id_to_name[task_id] = name
        self.task_name_to_id[name] = task_id

        return task_id

    def add_tasks(self, specs: list[TaskSpec[T]]) -> dict[str, int]:
        """
        Add a batch of tasks to the graph. The task names are the keys of the
        dictionary, and the values are tuples of (name, func, dependencies).

        Dependencies should be expressed using task names.

        :returns: a mapping from task names to task ids.
        """
        # We return a mapping from task names to task ids.
        task_name_to_id: dict[str, int] = {}

        for name, func, dependency_names in specs:
            dep_ids = [self.task_name_to_id[name] for name in dependency_names]
            self.add_task(name, func, dep_ids)
            task_name_to_id[name] = self.task_name_to_id[name]

        return task_name_to_id

    def get_task(self, task_id: int) -> Task[T]:
        return self.task_dag.get_node(task_id)

    def get_result(self, task_id: int) -> object:
        return self.task_id_to_result[task_id]

    def run(self) -> None:
        tasks_remaining = set(range(len(self.task_dag)))
        all_done = Event()

        logger.debug("Scanning dependency tree...")
        tasks_next: dict[int, set[int]] = {}
        for task_id in range(len(self.task_dag)):
            deps = self.task_dag.get_parents(task_id)
            tasks_next[task_id] = deps
            logger.debug(f"{task_id} <- {deps}.")

        # maybetodo: inject pool (allow for different pool implementations)
        with Pool() as pool:
            # pool = MultiprocessingPoolExecutor(_pool)

            def on_complete(task_id: int, result: T) -> None:
                nonlocal tasks_remaining

                # Store the result
                self.task_id_to_result[task_id] = Ok(result)

                # First, check if we're all done.
                tasks_remaining.remove(task_id)
                if not tasks_remaining:
                    all_done.set()
                    return

                # Otherwise, submit the tasks that were only waiting for this one.
                for next_task_id in self.task_dag.get_children(task_id):
                    s = tasks_next[next_task_id]
                    s.remove(task_id)
                    if not s:
                        logger.debug(f"All dependencies finished for {next_task_id}.")
                        submit(next_task_id)

            def on_error(task_id: int, error: BaseException) -> None:
                nonlocal tasks_remaining

                logger.debug(f"Task {task_id} failed: {error}")
                self.task_id_to_result[task_id] = Err(error)

                # Compute the set of tasks that depend on this one.
                pruned_tasks = self.task_dag.get_descendants(task_id)
                pruned_task_names = [self.get_task(task_id).name for task_id in pruned_tasks]
                logger.debug(f"Pruning tasks: {pruned_task_names}")

                # Remove the failed task and all of its descendants.
                tasks_remaining.remove(task_id)
                tasks_remaining = tasks_remaining.difference(pruned_tasks)

                # Then, check if we're all done.
                if not tasks_remaining:
                    all_done.set()
                    return

            def submit(task_id: int) -> None:
                task = self.get_task(task_id)
                pool.apply_async(
                    task.func,
                    args=[task.name],
                    callback=partial(on_complete, task_id),
                    error_callback=partial(on_error, task_id),
                )

            # Kick off the tasks that have no dependencies.
            for task_id in self.task_dag.get_roots():
                submit(task_id)
            all_done.wait()
