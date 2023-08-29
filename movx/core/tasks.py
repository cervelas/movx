import time
import threading
import traceback

from sqlalchemy import select, delete
import clairmeta

from movx.core import db

class TTask(threading.Thread):
    def __init__(self, task, task_func, **args):
        threading.Thread.__init__(self)
        self.task = task
        self.func = task_func
        self.daemon = True
        self.args = args
 
    def run(self):
        try:
            self.task.start()
            status, result = self.func(**self.args)
            self.task.done(status=status, result=result)
            #self.session.execute( update(Task).where(Task.id == self.task.id).values(progress=1) ) 
        except Exception as e:
            print(e)
            print( traceback.format_exc())
            self.task.done(status="Error", result={
                            "exception": str(e),
                            "traceback": traceback.format_exc()
                        })
             
    async def arun(self):
        try:
            self.task.start()
            status, result = self.func(**self.args)
            self.task.done(status=status, result=result)
            #self.session.execute( update(Task).where(Task.id == self.task.id).values(progress=1) ) 
        except Exception as e:
            print(e)
            print( traceback.format_exc())
            self.task.done(status="Error", result={
                            "exception": str(e),
                            "traceback": traceback.format_exc()
                        })

def probe_tasks_task(callback, status="inprogress"):
    post_prob_s = 2
    last_seen = time.perf_counter()
    start_at = time.time()

    while True:
        if time.perf_counter() - last_seen > post_prob_s:
            break
        
        tasks = db.Session.scalars( 
                select(db.Task).filter(db.Task.status == status) 
            ).all()
        if tasks is not None and len(tasks) > 0:
            last_seen = time.perf_counter()
            callback(tasks)
        
        time.sleep(0.5)

def ongoing():
    time.sleep(0.1)
    session = Session()
    with session:
        tasks = session.scalars( 
                select(db.Task).filter(db.Task.status == "inprogress") 
            ).all()
        if tasks is not None and len(tasks) > 0:
            return True
    return False

def print_cli_tasks_prog(tasks):
    for t in tasks:
        print("\x1b[1A\x1b[2K", end="")
    p = ""
    for t in tasks:
        p += "%s %0.f%% (eta: %0.fs)\r\n" % (t.name, t.progress*100, t.eta)
    print(p, end="")
    
def exec(task_func, task, wait=False, probe_cb=None, **args):
    ttask = TTask(task, task_func, **args)
    ttask.start()
    probe_tasks_thread = threading.Thread(target = probe_tasks_task, args = (probe_cb, ), daemon=True)
    time.sleep(0.3)
    probe_tasks_thread.start()
    if wait:
        probe_tasks_thread.join() 

    return True

def cancel():
    with db.Session() as session:
        tasks = session.scalars( 
                select(Task).filter(Task.status == "inprogress") 
            ).all()
        for t in tasks:
            t.status = "cancelled"
        session.commit()

def get_last_result(dcp, t="parse"):
    with db.session:
        task = db.session.scalars( 
                select(db.Task).where(db.Task.dcp_id == dcp.id).filter(db.Task.type==t).order_by(db.Task.last_update.desc()) 
            ).first()
        if task:
            return task.result
    
    return {}
