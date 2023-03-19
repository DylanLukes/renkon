import time
from dataclasses import dataclass
from functools import partial
from multiprocessing import Event, Pool
from pprint import pprint
from typing import Callable, Any, List

from renkon.util.dag import DAG


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

    job_dag: DAG[Job]

    def __init__(self):
        self.job_dag = DAG[Job]()

    def add_job(self, job: Job, dependencies: List[int]) -> int:
        job_id = self.job_dag.add_node(job, dependencies)
        return job_id

    def get_job(self, job_id: int) -> Job:
        return self.job_dag.get_node(job_id)

    def run(self):

        n_jobs_remaining = len(self.job_dag)
        all_done = Event()

        print("[main       ] Scanning job tree, dependencies are:")
        job_to_remaining_deps = {}
        for job_id in range(len(self.job_dag)):
            deps = self.job_dag.get_dependencies(job_id)
            job_to_remaining_deps[job_id] = deps
            print(
                f"[main       ]   Job {job_id} depends on Jobs {deps if deps else '{ }'}."
            )

        with Pool() as pool:

            def on_complete(job_id: int, result: Any):
                # First, check if we're all done.
                nonlocal n_jobs_remaining
                n_jobs_remaining -= 1
                if n_jobs_remaining == 0:
                    all_done.set()
                    return

                # Otherwise, submit the jobs that were only waiting for this one.
                for next_job_id in self.job_dag.get_dependents(job_id):
                    s = job_to_remaining_deps[next_job_id]
                    s.remove(job_id)
                    if not s:
                        print(
                            f"[main       ] Submitting unblocked Job {next_job_id}..."
                        )
                        submit(next_job_id)

            def submit(job_id: int):
                job = self.get_job(job_id)
                pool.apply_async(
                    job.func, args=[job.name], callback=partial(on_complete, job_id)
                )

            # Kick off the jobs that have no dependencies.
            for job_id in self.job_dag.get_roots():
                submit(job_id)
            all_done.wait(timeout=5)


def dummy_job(name):
    import os

    pid = os.getpid()
    print(f"[worker {pid}] Starting inference on {name}...", flush=True)
    time.sleep(0.5)
    print(f"[worker {pid}] Completed inference on {name}...", flush=True)


if __name__ == "__main__":
    r = Reactor()

    id1 = r.add_job(Job("Job 0", dummy_job), [])
    id2 = r.add_job(Job("Job 1", dummy_job), [id1])
    id3 = r.add_job(Job("Job 2", dummy_job), [])
    id4 = r.add_job(Job("Job 3", dummy_job), [id2, id3])
    id5 = r.add_job(Job("Job 4", dummy_job), [id4])

    r.run()
