import time
from pathlib import Path
import socket

import httpx
from sqlalchemy import delete as _delete, and_
from movx.core.db import Location, DCP, LocationType, Session

def scan_network(subnet, port):

    def connect(hostname, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(0.5)
        result = sock.connect_ex((hostname, port))
        sock.close()
        result == 0

    subnet = ".".join(subnet.split(".")[:2])

    for i in range(0,255):
        res = connect("%s." % str(i), 11011)
        if res:
            print("Device found at: ", "192.168.1."+str(i) + ":"+str(22))


def scan_agent(uri, path):

    paths = []

    uri = "http://%s/scan" % uri

    try:
        r = httpx.get(uri, params={"path": path})
        if r.status_code == 200:
            paths = r.json()
        else:
            raise Exception("Wrong response: %s" % r)
    except Exception as e:
        print("Error while scanning %s" % uri)
        print(e)
        raise e

    return [ Path(p) for p in paths ]

def scan_local(path):
    """
    Scan a location and create DCP.
    """

    path = Path(path).resolve().absolute()

    assetmaps = list(path.glob("**/ASSETMAP*"))
    
    return [ am.parent for am in assetmaps ]

def scan(location):

    if location.type == LocationType.Local:
        return scan_local(location.path)
    if location.type == LocationType.Agent:
        return scan_agent(location.uri, location.path)
    else:
        raise Exception("Cannot scan Location %s: Type Unknown" % location.name)

def scan_and_add(location):

    paths = scan(location)
    dcps = list(DCP.filter(DCP.location.has(id=location.id)).all())

    location.dcps_founds = len(list(paths))

    location.last_scan = time.time()

    for dcp in dcps:
        if dcp.path in paths:
            dcp.update( status = "present")
            paths.remove(dcp.path)
        else:
            dcp.update( status = "notfound")

    for path in paths:
        dcp = DCP(location=location, path=path, title=Path(path).name)
        dcp.add()
        dcps.append(dcp)

    return dcps

def scan_all():
    """
    Scan every locations for folders with ASSETMAP recursively
    """
    for location in Location.get():
        scan(location)


def delete_with_dcp(location):
    # deleteall
    with session:
        session.execute(_delete(DCP).where(DCP.location_id == location.id))
        session.execute(_delete(Location).where(Location.id == location.id))
        session.commit()
