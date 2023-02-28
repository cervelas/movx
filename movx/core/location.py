import os
from pathlib import Path

class Location:
    def __init__(self, name, path) -> None:
        self.name = name
        self.path = Path(path)
        self.enabled = True
        self.db = self.check_for_db()
        self.dcps = {}
        self.dcps_found = 0

    def check_for_db(self):
        parents = self.path.parents
        for p in parents[::-1]:
            db_file = p / "dcps.db"
            if db_file.is_file() and os.access(db_file, W_OK):
                return db_file
        return None

    def scan_dcps(self):
        self.dcps_found = 0
        print("scan for dcp in %s" % self.path.absolute())
        assetmaps = list(self.path.glob("**/ASSETMAP*"))
        self.dcps_founds = len(list(assetmaps))
        return list(assetmaps)

    def to_dict(self):
        return {
            "path": str(self.path),
            "name": str(self.name),
            "enabled": self.enabled,
        }

    def from_dict(d):
        l = Location(d["name"], d["path"])
        l.enabled = d["enabled"]
        return l