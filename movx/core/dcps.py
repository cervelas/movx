import time
import json
import logging
import httpx

from sqlalchemy import select
from sqlalchemy.orm.session import make_transient

import clairmeta
from movx.core import check_report_to_dict, init_check_profile

from movx.core.db import DCP, Job, LocationType, Movie, Session, User, JobType
from movx.core import jobs, finditem, check_profile_folder


clairmeta.logger.set_level(logging.WARNING)

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
    files = {
        am["FileName"]: {"__id": am["Info"]["AssetMap"]["Id"], "__type": "assetmap"}
        for am in report.get("assetmap_list", [])
    }
    files.update(
        {
            file: {"__id": uuid, "__type": "unknown"}
            for uuid, file in report.get("asset_list", {}).items()
        }
    )

    for k, v in files.items():
        f = finditem(report, "Id", v["__id"])
        for e in f:
            files[k].update(e)
        if "asdcpKind=" in files[k].get("Type", ""):
            files[k]["__type"] = files[k].get("Type").split("asdcpKind=")[1].lower()
        elif files[k].get("PackingList") is True:
            files[k]["__type"] = "pkl"

    files.update(
        {
            vi["FileName"]: {"__type": "volindex", **vi["Info"]}
            for vi in report.get("volindex_list", [])
        }
    )

    return files

def start_poll_agent_job(job, dcp, type, timeout = 20):
    ret = False
    started = time.time()
    uri = "http://%s/job_start" % dcp.location.uri
    r = httpx.get(uri, params={"type": type, "path": dcp.path})
    if r.status_code == 200:
        resp = r.json()
        finished = False
        uri = "http://%s/job_status" % dcp.location.uri
        while not finished:
            if time.time() - started > 20:
                raise Exception("Timeout on job status request")
            r = httpx.get(uri, params={"path": dcp.path})
            if r.status_code == 200:
                resp = r.json()
                if resp.get("status") == "done":
                    ret = resp.get("result", {}).get("report", {})
                    finished = True
            else:
                raise Exception("Bad response on job status request : %s" % r)
            time.sleep(2)
    else:
        raise Exception("Bad response on job start request: %s" % r)
    
    return ret

def parse_job(job, dcp, probe=False, kdm=None, pkey=None):
    """
    Parse a DCP
    """
    report = {}

    if dcp.location.type == LocationType.Agent:
        report = start_poll_agent_job(job, dcp, "parse")
    else:
        cm_dcp = clairmeta.DCP(dcp.path, kdm=kdm, pkey=pkey)
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


def probe(dcp, kdm=None, pkey=None):
    """
    Create and run a Probing job
    """
    job = Job(type=JobType.probe, dcp=dcp, author=User.get(1))

    job.add()

    make_transient(dcp)

    ttask = jobs.JobTask(job, parse_job, dcp=dcp, kdm=kdm, pkey=pkey, probe=True)

    ttask.start()

    # tasks.exec(_parse_task, task, wait_task=blocking, dcp = dcp, probe = probe)
    return job.id


def check_job(job, dcp, ov_dcp_path=None, profile="default.json"):
    """
    Check a DCP
    """
    report = {}
    status = False

    init_check_profile()

    if profile is None:
        with open(profile, "r") as fp:
            profile = json.load(fp)

    def check_job_cb(file, current, final, t):
        job.update(progress=current / final)

    cm_dcp = clairmeta.DCP(dcp.path)
    status, check_report = cm_dcp.check(
        profile=profile, ov_path=ov_dcp_path, hash_callback=check_job_cb
    )

    report = check_report_to_dict(check_report)

    job.finished.set()

    return report


def check(dcp, ov=None, profile=None, cb=None):
    """
    Create a Check job for a DCP
    """
    job = Job(type=JobType.check, dcp=dcp, author=User.get(1))

    job.add()

    # make_transient(dcp)

    ov_path = ov.path if ov else None

    profile = check_profile_folder / "%s.json" % profile

    jt = jobs.JobTask(job, check_job, dcp=dcp, ov_dcp_path=ov_path, profile=str(profile.resolve()))
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
            movie = Movie(title=movie_title)
            session.add(movie)
            session.commit()
        else:
            if movie.dcps:
                if dcp in movie.dcps():
                    return

        dcp.movie = movie
        session.commit()


def human_check_job(job, dcp):
    """
    Create a Human  job for a DCP
    """
    job = Job(type=JobType.check, dcp=dcp, author=User.get(1), progress=0)

    job.add()

    # make_transient(dcp)

    return job.id

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
