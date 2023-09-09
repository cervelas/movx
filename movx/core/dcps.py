import time

from sqlalchemy import select
from sqlalchemy.orm.session import make_transient
import clairmeta

from movx.core.db import DCP, Job, Movie, session
from movx.core import jobs, DEFAULT_CHECK_PROFILE


def check_all(cb=None):
    ids = []
    for dcp in DCP.get():
        ids.append(check(dcp, cb=cb))

    time.sleep(1)
    while True:
        time.sleep(1)
        if jobs.ongoing() is False:
            break
        time.sleep(1)

    with session:
        for id in ids:
            task = session.get(Job, id)
            print(task.status)
            if task.status == "error":
                print(task.result)
            # print(task.result)


def parse_all():
    ids = []
    for dcp in DCP.get():
        ids.append(parse(dcp))

    print("ongoing")
    while jobs.ongoing() is True:
        print("ongoing")
        time.sleep(2)

    with session:
        for id in ids:
            task = session.get(Job, id)
            print(task.status)
            # print(task.result)

        for dcp in session.scalars(select(DCP)).all():
            print(dcp.size)


def parse_task(job, dcp, probe=False):
    report = {}

    cm_dcp = clairmeta.DCP(dcp.path)
    report = cm_dcp.parse(probe=probe)

    dcp.update(
        package_type=report.get("package_type", "??"), size=report.get("size", 0)
    )

    if len(report.get("cpl_list", [])) > 0:
        cpl = report["cpl_list"][0]["Info"]["CompositionPlaylist"]

        update_movie(dcp, cpl["NamingConvention"]["FilmTitle"]["Value"])
        dcp.update(kind=cpl["ContentKind"])

    job.finished.set()

    return "success", report


def parse(dcp, probe=False):
    task = Job(type="parse", name="Parsing %s" % dcp.title, dcp=dcp, status="created")

    with session:
        session.add(task)
        session.commit()

    make_transient(dcp)

    ttask = jobs.JobTask(task, parse_task, dcp=dcp, probe=probe)
    
    ttask.start()

    # tasks.exec(_parse_task, task, wait_task=blocking, dcp = dcp, probe = probe)
    return task.id


def check_task(job, dcp, profile=None, cb=None):
    report = {}
    status = False
    profile = profile or DEFAULT_CHECK_PROFILE

    def check_cb(file, current, final, t):
        job.update(progress=current / final)

    cm_dcp = clairmeta.DCP(dcp.path)
    status, checkreport = cm_dcp.check(profile=profile, ov_path=None, hash_callback=check_cb)

    report = checkreport.to_dict()

    report["succeeded"] = [s.to_dict() for s in checkreport.checks_succeeded()]
    report["fails"] = [f.to_dict() for f in checkreport.checks_failed()]
    report["bypassed"] = [b.to_dict() for b in checkreport.checks_bypassed()]

    job.finished.set()

    return status, report

def check(dcp, profile=None, cb=None):
    job = Job(type="check", name="Check %s" % dcp.title, dcp=dcp, status="created")

    job.add()

    #make_transient(dcp)

    jt = jobs.JobTask(job, check_task, dcp=dcp, profile=profile)
    jt.start()

    # ttask.run()

    return job.id


def update_movie(dcp, movie_title):
    with session:
        movie = session.scalars(
            select(Movie).filter(Movie.title == movie_title)
        ).first()

        dcp = session.query(DCP).get(dcp.id)

        if movie is None:
            print("not found")
            movie = Movie(title=movie_title)
            session.add(movie)
            session.commit()
        else:
            if movie.dcps:
                print([d.title for d in movie.dcps])
                if dcp in movie.dcps:
                    return

        movie.dcps.append(dcp)
        session.commit()

def copy_task(dcp, target_folder):
    report = {}
    for f in dcp.files:
        report[f] = { "status": "ready", "progress": 0, "info": "", "size": 0 }
        '''
        if (Path(target_folder) / f).exists():
            //check size and crc
            if file is wrong, compare file bytes then complete copy if possible with manual copy
            // update status
        else:
            //copy the file using copy2 ?

        '''



def get_OVs(movie):
    ovs = []
    for dcp in movie.dcps:
        if dcp.type == "OV":
            ovs.append(dcp)
    return ovs


def get_VFs(movie):
    vfs = []
    for dcp in movie.dcps:
        if dcp.type == "VF":
            vfs.append(dcp)
    return vfs
