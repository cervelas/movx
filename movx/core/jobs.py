import time
import threading
import traceback
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm.session import make_transient

from movx.core import db
import movx.core.agent
from movx.core.agent import JobType
from movx.core.agent import JobStatus


class JobTask(threading.Thread):
    """
    Class that can manage a Job asynchronously.
    """

    poll_enable = threading.Event()
    poll_interval_s = 2
    prob_cb = False

    def __init__(self, job: db.Job, task_func: Callable, **args):
        threading.Thread.__init__(self)
        self.job = job
        self.job.__last_poll = 0
        self.job.finished = threading.Event()
        self.func = task_func
        self.daemon = True
        self.args = args

        self.cancelable = False
        self.is_paused = threading.Event()
        self.is_cancelled = threading.Event()

    def start_poll():
        if not JobTask.poll_enable.is_set():
            JobTask.poll_enable.clear()
            threading.Thread(target=JobTask.__poll_tasks)

    def pause(self):
        self.is_paused.set()

    def resume(self):
        self.is_paused.clear()

    def cancel(self):
        self.is_cancelled.set()

    def run(self):
        self.is_paused.clear()
        try:
            with self.job.fresh() as j:
                j.update(
                    status=movx.core.agent.JobStatus.started,
                    started_at=time.time(),
                )

            result = self.func(self.job, **self.args)
            # JobTask.start_poll()

            while not self.is_cancelled.wait(timeout=1):
                if self.job.finished.wait(timeout=0.5):
                    with self.job.fresh() as j:
                        j.update(
                            status=movx.core.agent.JobStatus.finished,
                            progress=1,
                            result=result or {},
                            finished_at=time.time(),
                        )
                    break

            if self.is_cancelled.is_set():
                with self.job.fresh() as j:
                    j.update(
                        status=movx.core.agent.JobStatus.cancelled,
                        finished_at=time.time(),
                    )

            # self.session.execute( update(Task).where(Task.id == self.task.id).values(progress=1) )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.job.update(
                status=movx.core.agent.JobStatus.errored,
                result={"exception": str(e), "traceback": traceback.format_exc()},
                finished_at=time.time(),
            )

def ongoing():
    time.sleep(0.1)
    with db.Session() as session:
        tasks = session.scalars(
            select(db.Job).filter(db.Job.status == "inprogress")
        ).all()
        if tasks is not None and len(tasks) > 0:
            return True
    return False


def print_cli_tasks_prog(tasks):
    for t in tasks:
        print("\x1b[1A\x1b[2K", end="")
    p = ""
    for t in tasks:
        p += "%s %0.f%% (eta: %0.fs)\r\n" % (t.name, t.progress * 100, t.eta)
    print(p, end="")


def mockup_job(job, duration=60):
    """
    Check a DCP
    """

    def job_cb(progress):
        print("cb", progress)
        with job.fresh() as _job:
            _job.update(progress=progress)

    for i in range(0, duration):
        time.sleep(0.5)
        job_cb(i / duration)

    job.finished.set()

    return { "status": "finished" }


def mock(dcp):
    """
    Create and run a Mocking job
    """
    
    job = db.Job(type=movx.core.agent.JobType.mockup, dcp=dcp, author=db.User.get(1))

    job.add()

    ttask = JobTask(job, mockup_job)

    ttask.start()

    # tasks.exec(_parse_task, task, wait_task=blocking, dcp = dcp, probe = probe)
    return job.id