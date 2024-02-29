import enum
from http.client import HTTPException
import os
import logging
from pathlib import Path
import threading
import time
import traceback
import socket
from dataclasses import dataclass, field
import uuid

import clairmeta

from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from movx.core import (
    is_linux,
    is_win,
    DEFAULT_CHECK_PROFILE,
    check_report_to_dict,
    version,
)
from movx.gui import get_linux_drives, get_windows_drives

clairmeta.logger.set_level(logging.WARNING)


class JobType(enum.Enum):
    test = 0
    parse = 1
    probe = 2
    check = 3
    copy = 4
    mockup = 99
    none = None


class JobStatus(enum.Enum):
    errored = 0
    created = 1
    started = 2
    running = 3
    finished = 4
    cancelled = 5
    unknown = 666
    none = None

@dataclass
class AgentJob:
    path: str
    type: JobType
    status: JobStatus = JobStatus.created
    progress: float = 0
    result: dict = field(default_factory=lambda: {})
    created: time = time.time()
    uuid: str = str(uuid.uuid4())

    def to_dict(self):
        d = self.__dict__.copy()
        d.update({ "type": self.type.value, "status": self.status.value })
        return d

def root_path():
    if os.environ.get("MOVX_AGENT_ROOT_PATH"):
        return Path(os.environ.get("MOVX_AGENT_ROOT_PATH"))
    else:
        return None


logger = logging.getLogger("MovX.Agent")

__jobs = []

def new_job(path, jobtype):
    global __jobs
    aj = AgentJob(path, jobtype)
    aj.uuid = str(uuid.uuid4())
    __jobs.append(aj)
    return aj

def index(request):
    return JSONResponse({"root_path": str(root_path().resolve()), "version": version})

def parse(aj, probe=False, kdm=None, pkey=None):
    """
    Parse a DCP
    """

    print("parse starting on %s" % aj.path)


    try:
        cm_dcp = clairmeta.DCP(aj.path, kdm=kdm, pkey=pkey)
        report = cm_dcp.parse(probe=probe)

        aj.status = JobStatus.finished
        aj.progress = 1
        aj.result = {"report": report}

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        aj.status = JobStatus.errored
        aj.result = traceback.format_exc()

    print("parse finished on %s" % aj.path)


def check(aj, ov_dcp_path=None, profile=None, kdm=None, pkey=None):
    """
    Check a DCP
    """
    report = {}
    status = False

    profile = profile or DEFAULT_CHECK_PROFILE

    print("Check starting on %s" % aj.path)

    def check_job_cb(file, current, final, t):
        nonlocal aj
        aj.progress = current / final

    try:
        cm_dcp = clairmeta.DCP(aj.path, kdm=kdm, pkey=pkey)
        status, check_report = cm_dcp.check(
            profile=profile, ov_path=ov_dcp_path, hash_callback=check_job_cb
        )

        aj.status = JobStatus.finished
        aj.progress = 1
        aj.result = {"status": status, "report": check_report_to_dict(check_report)}

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        aj.status = JobStatus.errored
        aj.result = traceback.format_exc()

    print("Check finished on %s" % aj.path)


def browse(request):
    path = request.query_params.get("path")
    dirs = []
    if not path:
        if is_win():
            dirs = get_windows_drives()
        elif is_linux():
            dirs = get_linux_drives()
    else:
        if root_path():
            path = root_path() / path
        dirs = [
            str(Path(x).relative_to(path)) for x in Path(path).iterdir() if x.is_dir()
        ]
    return JSONResponse(dirs)


def scan(request):
    path = request.query_params.get("path", ".")
    dcps = []

    if root_path():
        path = root_path() / path

    path = Path(path).resolve().absolute()

    assetmaps = list(path.glob("**/ASSETMAP*"))

    dcps = [str(am.parent.resolve()) for am in assetmaps]

    return JSONResponse(dcps)


async def job_start(request):
    path = request.query_params.get("path")
    type = request.query_params.get("type")

    json = {}
    try:
        json = await request.json()
    except:
        pass

    if path:
        if type == "parse":
            aj = new_job(path, JobType.parse)
            t = threading.Thread(
                target=parse,
                args=(aj, False, json.get("kdm_path"), json.get("dkdm_path")),
            ).start()
            return JSONResponse(aj.to_dict())
        elif type == "probe":
            aj = new_job(path, JobType.probe)
            t = threading.Thread(
                target=parse,
                args=(aj, True, json.get("kdm_path"), json.get("dkdm_path")),
            ).start()
            return JSONResponse(aj.to_dict())
        elif type == "check":
            aj = new_job(path, JobType.check)
            t = threading.Thread(
                target=check,
                args=(
                    aj,
                    json.get("ov_dcp_path"),
                    json.get("profile"),
                    json.get("kdm_path"),
                    json.get("dkdm_path"),
                ),
            ).start()
            return JSONResponse(aj.to_dict())
        else:
            return JSONResponse({"Error": "type %s not found" % type})
    else:
        return JSONResponse({"Error": "path %s not found" % path})

    return JSONResponse({"Success": "Started task %s on %s" % (type, path)})


def job_status(request):
    _uuid = request.query_params.get("uuid")
    global __jobs
    for j in __jobs:
        if _uuid == j.uuid:
            return JSONResponse(j.to_dict())

    return Response("Job with UUID %s not Found" % _uuid, 404)


def job_cancel(request):
    path = request.query_params.get("path")
    type = request.query_params.get("type")
    return JSONResponse(current_jobs.get(path))


def startup():
    ip = get_ip()
    print("Started Agent @ http://%s:11011" % ip)
    print("Call get /exit to quit")


routes = [
    Route("/", index),
    Route("/browse", browse),
    Route("/scan", scan),
    Route("/job_start", job_start, methods=["POST", "GET"]),
    Route("/job_status", job_status),
    Route("/exit", lambda: exit(0))
    # Mount('/static', StaticFiles(directory="static")),
]

app = Starlette(debug=False, routes=routes, on_startup=[startup])


def get_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    IP = ""
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP
