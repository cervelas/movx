import time
from pathlib import Path

from sqlalchemy import select, delete as _delete
from movx.core.db import Location, DCP, session, Session


def scan(location):
    """
    Scan a location and create DCP.
    """
    location.dcps_found = 0

    path = Path(location.path).resolve().absolute()

    assetmaps = list(path.glob("**/ASSETMAP*"))

    location.dcps_founds = len(list(assetmaps))

    location.last_scan = time.time()

    dcps = []

    for path in assetmaps:
        dcp = DCP.filter(DCP.path == str(path.parent)).first()

        if not dcp:
            dcp = DCP(location=location, path=str(path.parent), title=path.parent.name)
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
