import threading
import time
from pathlib import Path
import socket

import httpx
from sqlalchemy import delete as _delete, and_
from movx.core import version
from movx.core.db import Location, DCP, LocationType, Session


def scan_network(subnet, port):
    def connect(hostname, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(0.5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        result == 0

    subnet = ".".join(subnet.split(".")[:2])

    for i in range(0, 255):
        res = connect("%s." % str(i), 11011)
        if res:
            print("Device found at: ", "192.168.1." + str(i) + ":" + str(22))


def agent_infos(uri):
    infouri = "http://%s" % uri

    r = httpx.get(infouri)
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Wrong response: %s" % r)


def scan_agent(uri, path):
    paths = []

    agent_version = agent_infos(uri)["version"]

    if agent_version != version:
        raise Exception(
            "Version mismatch! Agent is %s, host is %s" % (agent_version, version)
        )

    scanuri = "http://%s/scan" % uri

    try:
        r = httpx.get(scanuri, params={"path": path})
        if r.status_code == 200:
            paths = r.json()
        else:
            raise Exception("Wrong response: %s" % r)
    except Exception as e:
        print("Error while scanning %s" % scanuri)
        print(e)
        raise e

    return [Path(p) for p in paths]


def scan_local(path):
    """
    Scan a location and create DCP.
    """

    path = Path(path).resolve().absolute()

    assetmaps = list(path.glob("**/ASSETMAP*"))

    return [am.parent for am in assetmaps]


def get_root_path(location):
    if location.type == LocationType.Local:
        return Path.cwd()
    if location.type == LocationType.Agent:
        return agent_infos()["root_path"]
    else:
        raise Exception("Cannot get Root path for %s: Type Unknown" % location.name)


def __scan(location):
    if location.type == LocationType.Local:
        return scan_local(location.path)
    if location.type == LocationType.Agent:
        return scan_agent(location.uri, location.path)
    else:
        raise Exception("Cannot Scan Location %s: Type Unknown" % location.name)

def scan_add_dcps(location):

    paths = __scan(location)
    dcps = list(DCP.filter(DCP.location.has(id=location.id)).all())

    location.dcps_founds = len(list(paths))

    location.last_scan = time.time()

    for dcp in dcps:
        if Path(dcp.path) in paths:
            dcp.update(status="present")
            paths.remove(Path(dcp.path))
        else:
            dcp.delete()

    with location.fresh() as _loc:
        for path in paths:
            dcp = DCP(location=_loc, path=str(path.resolve()), title=Path(path).name)
            dcp.add()
            dcps.append(dcp)

    return dcps


def scan_all():
    """
    Scan every locations for folders with ASSETMAP recursively
    """
    for location in Location.get():
        scan_add_dcps(location)

