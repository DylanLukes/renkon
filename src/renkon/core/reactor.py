from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class Job:
    name: str
    func: Callable[..., Any]


class Reactor:
    """
    Implements a job queue with dependencies using python multiprocessing.

    Name is just a core/reactor joke, unrelated to the reactor pattern or twisted.

    h/t: https://stackoverflow.com/questions/75574947/job-queue-with-dependencies-with-python-multiprocessing
    """
