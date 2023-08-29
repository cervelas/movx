import time
from pathlib import Path

from sqlalchemy import select, delete as _delete
from movx.core.db import Location, DCP, session, Session


def add(path, name, type="Drive"):
    loc = Location(path=path, name=name, type=type)

    with session:
        session.add(loc)
        session.commit()

    return loc


def get_all():
    return Session.scalars(select(Location)).all()


def get(id):
    return Session.get(Location, id)


def get_name(name):
    return Session.scalars(select(Location).where(Location.name == name)).first()


def delete(location):
    # deleteall
    with session:
        session.execute(_delete(DCP).where(DCP.location_id == location.id))
        session.execute(_delete(Location).where(Location.id == location.id))
        session.commit()


def scan(location):
    location.dcps_found = 0

    path = Path(location.path).resolve().absolute()

    assetmaps = list(path.glob("**/ASSETMAP*"))

    location.dcps_founds = len(list(assetmaps))

    location.last_scan = time.time()

    for path in assetmaps:
        dcp = session.scalars(select(DCP).filter(DCP.path == str(path.parent))).first()

        if not dcp:
            session.add(
                DCP(location=location, path=str(path.parent), title=path.parent.name)
            )
            session.commit()


def scan_all():
    """
    Scan every locations for folders with ASSETMAP recursively
    """
    for location in get_all():
        scan(location)

    """
    for dcp in self.dcps:
        if dcp.package_type != "OV":
            ovs = self.get_ov_dcps(dcp.title)
            if len(ovs) == 1:
                dcp.ov_path = ovs[0].path

    self.dcps = [ dcp for dcp in self.dcps if dcp.path.exists() ]
    """


# default_location = Location("Current Directory", ".")
