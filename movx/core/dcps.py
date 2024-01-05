import time
from pathlib import Path
import json

from sqlalchemy import select
from sqlalchemy.orm.session import make_transient
import clairmeta

from movx.core.db import DCP, Job, Movie, Session, User, JobType
from movx.core import jobs, DEFAULT_CHECK_PROFILE, finditem

check_profile_file = Path.home() / ".movx" / "check_profile.json"

if not check_profile_file.exists():
    with open(check_profile_file, "w") as fp:
        json.dump(DEFAULT_CHECK_PROFILE, fp)




def check_all(cb=None):
    """
    Check all the DCP in the database
    """
    ids = []
    for dcp in DCP.get():
        ids.append(check(dcp, cb=cb))

    time.sleep(1)
    while True:
        time.sleep(1)
        if jobs.ongoing() is False:
            break
        time.sleep(1)

    with Session() as session:
        for id in ids:
            task = session.get(Job, id)
            print(task.status)
            if task.status == "error":
                print(task.result)
            # print(task.result)


def parse_all():
    """
    Probe all the DCP^s in the database
    """
    ids = []
    for dcp in DCP.get():
        ids.append(parse(dcp))

    print("ongoing")
    while jobs.ongoing() is True:
        print("ongoing")
        time.sleep(2)

    with Session() as session:
        for id in ids:
            task = session.get(Job, id)
            print(task.status)
            # print(task.result)

        for dcp in session.scalars(select(DCP)).all():
            print(dcp.size)

def by_files_parse_report(report):
    
    files = { am["FileName"]: { "__id": am["Info"]["AssetMap"]["Id"], "__type": "assetmap" } for am in report["assetmap_list"] }
    files.update({ file: { "__id": uuid, "__type": "unknown" } for uuid, file in report["asset_list"].items() })

    for k, v in files.items():
        f = finditem(report, "Id", v["__id"])
        for e in f:
            files[k].update( e )
        if "asdcpKind=" in files[k].get("Type", ""):
            files[k]["__type"] = files[k].get("Type").split("asdcpKind=")[1].lower()
        elif files[k].get("PackingList") is True:
            files[k]["__type"] = "pkl"

    files.update({ vi["FileName"]: { "__type": "volindex", **vi["Info"] } for vi in report["volindex_list"] })

    return files

def parse_job(job, dcp, probe=False):
    """
    Parse a DCP
    """
    report = {}

    cm_dcp = clairmeta.DCP(dcp.path)
    report = cm_dcp.parse(probe=probe)

    dcp.update(
        package_type=report.get("package_type", "??"), size=report.get("size", -1)
    )
    
    report["files"] = by_files_parse_report(report)

    if len(report.get("cpl_list", [])) > 0:
        cpl = report["cpl_list"][0]["Info"]["CompositionPlaylist"]

        update_movie(dcp, cpl["NamingConvention"]["FilmTitle"]["Value"])

        dcp.update(kind=cpl["ContentKind"])
    else:
        update_movie(dcp, dcp.title.split("_")[0])

    job.finished.set()

    return report


def parse(dcp):
    """
    Create and run a Probing job
    """
    job = Job(type=JobType.parse, dcp=dcp, author=User.get(1))

    job.add()

    make_transient(dcp)

    ttask = jobs.JobTask(job, parse_job, dcp=dcp, probe=False)

    ttask.start()

    # tasks.exec(_parse_task, task, wait_task=blocking, dcp = dcp, probe = probe)
    return job.id

def probe(dcp):
    """
    Create and run a Probing job
    """
    job = Job(type=JobType.probe, dcp=dcp, author=User.get(1))

    job.add()

    make_transient(dcp)

    ttask = jobs.JobTask(job, parse_job, dcp=dcp, probe=True)

    ttask.start()

    # tasks.exec(_parse_task, task, wait_task=blocking, dcp = dcp, probe = probe)
    return job.id



def check_job(job, dcp, profile=None, cb=None):
    """
    Check a DCP
    """
    report = {}
    status = False
    profile = DEFAULT_CHECK_PROFILE
    with open(check_profile_file, "r") as fp:
        profile = json.load(fp)

    def check_job_cb(file, current, final, t):
        job.update(progress=current / final)

    cm_dcp = clairmeta.DCP(dcp.path)
    status, checkreport = cm_dcp.check(
        profile=profile, ov_path=None, hash_callback=check_job_cb
    )

    report = checkreport.to_dict()

    report["succeeded"] = [s.to_dict() for s in checkreport.checks_succeeded()]
    report["fails"] = [f.to_dict() for f in checkreport.checks_failed()]
    report["errors"] = [v.to_dict() for v in checkreport.checks_failed() if v.errors[0].criticality == "ERROR"]
    report["warnings"] = [v.to_dict() for v in checkreport.checks_failed() if v.errors[0].criticality == "WARNING"]
    report["bypassed"] = [b.to_dict() for b in checkreport.checks_bypassed()]


    job.finished.set()

    return report


def check(dcp, profile=None, cb=None):
    """
    Create a Check job for a DCP
    """
    job = Job(type=JobType.check, dcp=dcp,  author=User.get(1))

    job.add()

    # make_transient(dcp)

    jt = jobs.JobTask(job, check_job, dcp=dcp, profile=profile)
    jt.start()

    return job.id


def update_movie(dcp, movie_title):
    """
    Update a DCP with an existing movie or not
    """
    with Session() as session:
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
                if dcp in movie.dcps():
                    return

        dcp.movie = movie
        session.commit()


def copy_task(dcp, target_folder):
    """
    Copy a DCP from one location to another
    """
    report = {}
    for f in dcp.files:
        report[f] = {"status": "ready", "progress": 0, "info": "", "size": 0}
        """
        if (Path(target_folder) / f).exists():
            //check size and crc
            if file is wrong, compare file bytes then complete copy if possible with manual copy
            // update status
        else:
            //copy the file using copy2 ?

        """
