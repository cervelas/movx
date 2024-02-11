
import os
import logging
from pathlib import Path
import threading
import traceback
import socket

import clairmeta

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.routing import Route, Mount, WebSocketRoute
from starlette.background import BackgroundTask

from movx.core import is_linux, is_win, DEFAULT_CHECK_PROFILE, check_report_to_dict, version
from movx.gui import get_linux_drives, get_windows_drives

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def root_path():
    if os.environ.get("MOVX_AGENT_ROOT_PATH"):
        return Path(os.environ.get("MOVX_AGENT_ROOT_PATH"))
    else:
        return None

logger = logging.getLogger("MovX.Agent")

current_jobs = {}

def parse(path, probe=False, kdm=None, pkey=None):
    """
    Parse a DCP
    """

    print("parse starting on %s" % path)

    current_jobs.update({ path: {"status": "created", "progress": 0 } })
    try:
        cm_dcp = clairmeta.DCP(path, kdm=kdm, pkey=pkey)
        report = cm_dcp.parse(probe=probe)

        current_jobs[path].update({ "status": "done", "result": {"report": report}, "progress": 1 })

    except Exception as e:
        print(e)
        print(traceback.format_exc())
        current_jobs[path].update({ "status": "error", "Error": traceback.format_exc() })

    print("parse finished on %s" % path)

def check(path, ov_dcp_path=None, profile=None):
    """
    Check a DCP
    """
    report = {}
    status = False

    global current_jobs
    current_jobs.update({ path: {"status": "created", "progress": 0} })

    profile = profile or DEFAULT_CHECK_PROFILE

    
    def check_job_cb(file, current, final, t):
        global current_jobs
        nonlocal path
        print(current / final)
        current_jobs[path].update({ "progress": current / final })

    try:
        cm_dcp = clairmeta.DCP(path)
        status, check_report = cm_dcp.check(
            profile=profile, ov_path=ov_dcp_path, hash_callback=check_job_cb
        )

        result = {"status": status, "report": check_report_to_dict(check_report) }

        current_jobs[path].update({ "status": "done", "result": result, "progress": 1 })

    except Exception as e:

        print(e)
        print(traceback.format_exc())
        current_jobs[path].update({ "status": "error", "Error": traceback.format_exc() })

    print("parse finished on %s" % path)

def index(request):
    return JSONResponse({ "root_path": root_path(), "version": version })

def browse(request):
    path = request.query_params.get('path')
    dirs = []
    if not path:
        if is_win():
            dirs = get_windows_drives()
        elif is_linux():
            dirs = get_linux_drives()
    else:
        if root_path():
            path = root_path() / path
        dirs = [str(Path(x).relative_to(path)) for x in Path(path).iterdir() if x.is_dir()]
    return JSONResponse(dirs)

def scan(request):
    path = request.query_params.get('path')
    dcps = []
    if path:
        if root_path():
            path = root_path() / path
            
        path = Path(path).resolve().absolute()

        assetmaps = list(path.glob("**/ASSETMAP*"))

        dcps = [ str(am.parent.resolve()) for am in assetmaps ]

    return JSONResponse(dcps)

async def job_start(request):
    path = request.query_params.get('path')
    type = request.query_params.get('type')

    json = {}
    try:
        json = await request.json()
    except:
        pass
        
    if path:
        if type == "parse":
            t = threading.Thread(target=parse, args=(path, False, json.get("kdm_path"), json.get("dkdm_path"))).start()
        elif type == "probe":
            t = threading.Thread(target=parse, args=(path, True, json.get("kdm_path"), json.get("dkdm_path"))).start()
        elif type == "check":
            t = threading.Thread(target=check, args=(path, json.get("ov_dcp_path"), json.get("profile"))).start()
        else:
            return JSONResponse({"Error": "type %s not found" % type})
    else:
        return JSONResponse({"Error": "path %s not found" % path})

    return JSONResponse({"Success": "Started task %s on %s" % (type, path)})

def job_status(request):
    global current_jobs
    path = request.query_params.get('path')
    if path:
        return JSONResponse(current_jobs.get(path))

    return JSONResponse(current_jobs)

def job_cancel(request):
    path = request.query_params.get('path')
    type = request.query_params.get('type')
    return JSONResponse(current_jobs.get(path))

def startup():
    ip = get_ip()
    print('Started Agent @ http://%s:11011' % ip)
    print("Call get /exit to quit")

routes = [
    Route('/', index),
    Route('/path', path),
    Route('/browse', browse),
    Route('/scan', scan),
    Route('/job_start', job_start),
    Route('/job_status', job_status),
    Route('/exit', lambda: exit(0))
    #Mount('/static', StaticFiles(directory="static")),
]

app = Starlette(debug=False, routes=routes, on_startup=[startup])