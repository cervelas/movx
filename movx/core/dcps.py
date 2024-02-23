import time
import json
import logging
import httpx

from sqlalchemy import select
from sqlalchemy.orm.session import make_transient

import clairmeta
from movx import dotmovx
from movx.core import check_report_to_dict

from movx.core.db import DCP, Job, LocationType, Movie, Session, User, JobType
from movx.core import jobs, finditem, DEFAULT_CHECK_PROFILE

clairmeta.logger.set_level(logging.WARNING)

check_profile_folder = dotmovx / "check_profiles"

default_check_profile = check_profile_folder / "default.json"


def init_check_profile():
    check_profile_folder.mkdir(exist_ok=True)

    if not default_check_profile.exists():
        with open(default_check_profile, "w") as fp:
            json.dump(DEFAULT_CHECK_PROFILE, fp)


def get_available_check_profiles():
    init_check_profile()

    profiles = []

    for f in check_profile_folder.iterdir():
        if f.is_file():
            profiles.append(f)

    return profiles


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
    Probe all the DCP's in the database
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


def by_files_parse_report(report):
    files = {
        am["FileName"]: {"__id": am["Info"]["AssetMap"]["Id"], "__type": "ASSETMAP"}
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
        if files[k].get("EssenceType") is not None:
            files[k]["__type"] = files[k].get("EssenceType")
        elif "asdcpKind=" in files[k].get("Type", ""):
            files[k]["__type"] = files[k].get("Type").split("asdcpKind=")[1].lower()
        elif files[k].get("PackingList") is True:
            files[k]["__type"] = "PKL"
        elif files[k].get("NamingConvention") is not None:
            files[k]["__type"] = "CPL"

    files.update(
        {
            vi["FileName"]: {"__type": "VOLINDEX", **vi["Info"]}
            for vi in report.get("volindex_list", [])
        }
    )

    return files


def start_poll_agent_job(job, dcp, type, timeout=3600, data=None):
    ret = False
    started = time.time()
    uri = "http://%s/job_start" % dcp.location.uri
    print(data)
    r = httpx.post(uri, params={"type": type, "path": dcp.path}, json=data)
    if r.status_code == 200:
        resp = r.json()
        finished = False
        uri = "http://%s/job_status" % dcp.location.uri
        while not finished:
            if time.time() - started > timeout:
                raise Exception("Timeout on job status request")
            r = httpx.get(uri, params={"path": dcp.path})
            if r.status_code == 200:
                resp = r.json()
                job.update(progress=resp.get("progress"))
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
        report = start_poll_agent_job(
            job, dcp, "parse", data={"kdm": kdm, "pkey": pkey}
        )
    elif dcp.location.type == LocationType.Local:
        cm_dcp = clairmeta.DCP(dcp.path, kdm=kdm, pkey=pkey)
        report = cm_dcp.parse(probe=probe)

    report["files"] = by_files_parse_report(report)

    report["movx_parse_probe"] = probe
    report["movx_parse_kdm"] = kdm
    report["movx_parse_pkey"] = pkey

    update_dcp_infos(dcp, report)

    job.finished.set()

    return report


def parse(dcp):
    """
    Create and run a Probing job
    """
    job = Job(type=JobType.parse, dcp=dcp, author=User.get(1))

    job.add()

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

    ttask = jobs.JobTask(job, parse_job, dcp=dcp, kdm=kdm, pkey=pkey, probe=True)

    ttask.start()

    # tasks.exec(_parse_task, task, wait_task=blocking, dcp = dcp, probe = probe)
    return job.id


def check_job(job, dcp, ov_dcp_path=None, profile=None, kdm=None, pkey=None):
    """
    Check a DCP
    """
    report = {}
    status = False
    _profile = {}

    profile = profile or default_check_profile

    with open(profile, "r") as fp:
        _profile = json.load(fp)

    if dcp.location.type == LocationType.Agent:
        report = start_poll_agent_job(
            job,
            dcp,
            "check",
            data={
                "ov_dcp_path": ov_dcp_path,
                "profile": _profile,
                "kdm": kdm,
                "pkey": pkey,
            },
        )
    elif dcp.location.type == LocationType.Local:

        def check_job_cb(file, current, final, t):
            job.update(progress=current / final)

        cm_dcp = clairmeta.DCP(dcp.path, kdm=kdm, pkey=pkey)
        status, check_report = cm_dcp.check(
            profile=_profile, ov_path=ov_dcp_path, hash_callback=check_job_cb
        )

        report = check_report_to_dict(check_report)

    report["movx_check_profile"] = str(profile)
    report["movx_check_ov"] = str(ov_dcp_path)
    report["movx_check_kdm"] = str(kdm)
    report["movx_check_pkey"] = str(pkey)

    job.finished.set()

    return report


def check(dcp, ov=None, profile=None, cb=None):
    """
    Create a Check job for a DCP
    """

    job = Job(type=JobType.check, dcp=dcp, author=User.get(1))

    job.add()

    init_check_profile()

    ov_path = ov.path if ov else None

    jt = jobs.JobTask(job, check_job, dcp=dcp, ov_dcp_path=ov_path, profile=profile)
    jt.start()

    return job.id


def update_movie(dcp, movie_title):
    """
    Update a DCP with an existing movie or not
    """
    movie = Movie.filter(Movie.title == movie_title).first()

    dcp = DCP.get(dcp.id)

    if movie is None:
        movie = Movie(title=movie_title)
        movie.add()
    else:
        if movie.dcps:
            if dcp in movie.dcps():
                return None

    with dcp.fresh() as _dcp:
        _dcp.movie = movie


def update_dcp_infos(dcp, report):
    dcp = dcp.update(
        package_type=report.get("package_type", "??"), size=report.get("size_bytes", -1)
    )

    cpl = False
    if len(report.get("cpl_list", [])) > 0:
        cpl = report["cpl_list"][0]["Info"]["CompositionPlaylist"]

    if cpl:
        update_movie(dcp, cpl["NamingConvention"]["FilmTitle"]["Value"])

        with dcp.fresh() as _dcp:
            _dcp.update(kind=cpl["ContentKind"])
    else:
        update_movie(dcp, dcp.title.split("_")[0])


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
