import time
import threading
import traceback

from sqlalchemy import select

from movx.core import db


class JobTask(threading.Thread):

    probe_enable = threading.Event()
    probe_interval_s = 2
    prob_cb = False

    def __init__(self, job, task_func, **args):
        threading.Thread.__init__(self)
        self.job = job
        self.job.__last_probe = 0
        self.func = task_func
        self.daemon = True
        self.args = args
        
        self.cancelable = False
        self.is_paused = threading.Event()
        self.job.finished = threading.Event()

    def start_probe():
        if not JobTask.probe_enable.is_set():
            JobTask.probe_enable.clear()
            threading.Thread(target=JobTask.__probe_tasks)

    def pause(self):
        self.is_paused.set()

    def resume(self):
        self.is_paused.clear()

    def run(self):
        self.is_paused.clear()
        try:
            self.job.update(
                progress=0, status="started", timestamp=time.time(), created_at=time.time()
            )
            JobTask.start_probe()

            while not self.job.finished.wait(timeout=1):
                status, result = self.func(self.job, **self.args)
                self.job.update(
                    progress=1,
                    status=status,
                    result=result or {"no result"},
                    eta=0,
                    elapsed_time_s=time.time() - self.job.timestamp,
                )

            # self.session.execute( update(Task).where(Task.id == self.task.id).values(progress=1) )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.job.update(
                status="Error",
                result={"exception": str(e), "traceback": traceback.format_exc()},
            )

    @classmethod
    def __probe_tasks(self):
        while JobTask.prob_enable.wait(timeout=JobTask.probe_interval_s):
            jobs = db.Job.get_all()
            for job in jobs:
                if job.eta > 0:
                    prog = round(job.progress, 2)
                    if prog >= 1 :
                        eta = 0
                    elif prog > 0:
                        eta = (1-prog) / ((prog) / job.timestamp) + 1
                    job.update(eta = eta, timestamp=time.time())

def ongoing():
    time.sleep(0.1)
    with db.session:
        tasks = db.session.scalars(
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


def exec(task_func, task, wait=False, probe_cb=None, **args):
    ttask = JobTask(task, task_func, **args)
    ttask.start()
    probe_tasks_thread = threading.Thread(
        target=probe_tasks_task, args=(probe_cb,), daemon=True
    )
    time.sleep(0.3)
    probe_tasks_thread.start()
    if wait:
        probe_tasks_thread.join()

    return True


def cancel():
    with db.Session() as session:
        tasks = db.Job.get_all()
        for t in tasks:
            t.status = "cancelled"
        session.commit()


def get_last_result(dcp, t="parse"):

    with db.Session() as session:
        task = session.scalars(
            select(db.Job)
            .where(db.Job.dcp_id == dcp.id)
            .filter(db.Job.type == t)
            .order_by(db.Job.last_update.desc())
        ).first()
        if task:
            return task.result

    return {}
