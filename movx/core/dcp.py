import pprint
import json
import uuid
from pathlib import Path

from movx.core.location import Location

import clairmeta

class DCP:
    def __init__(self, folder, rel_to, location):
        self.path = Path(folder)
        self.rel_to = rel_to
        self.rel_path = self.path.relative_to(rel_to)
        self.location = location
        self.full_title = self.path.name
        self.uid = uuid.uuid5(uuid.NAMESPACE_X500, str(self.path.absolute())) #"%s-%s-%s" % (self.location, self.rel_path, self.full_title)
        self.title = self.full_title.split('_')[0]
        self.package_type = self.full_title.split('_')[-1]
        self.status = None
        self.report = {}
        self.kind = None
        self.size = None
        self.namings = {}
        self.metadata = {}
        self.ov_path = None
        self.dcp = clairmeta.DCP(self.path.absolute())

    def asset(self, id):
        for a in self.assets:
            if a.id == str(id):
                return a
        return None
    
    def parse(self):
        try:
            self.dcp._parsed = False
            self.dcp._probeb = True
            self.metadata = self.dcp.parse()
            self.package_type = self.metadata.get("package_type", "Unknown")
            self.size = self.metadata.get("size", "Unknown")

            if len(self.metadata.get("cpl_list", [])) > 0:
                self.namings = self.metadata["cpl_list"][0]["Info"]["CompositionPlaylist"]["NamingConvention"]
                self.kind = self.metadata["cpl_list"][0]["Info"]["CompositionPlaylist"]["ContentKind"]

        except Exception as e:
            print(e)

    def check(self, ov=None, cb=None):
        status, report = self.dcp.check( ov_path=ov,
        hash_callback=cb)
        
        for c in report.checks_failed():
            pprint.pprint(c.short_desc())
            pprint.pprint([ e.message for e in c.errors ])


        self.report = report.to_dict()

        return report

    def to_dict(self):
        return {
            "title": str(self.title),
            "path": str(self.path),
            "rel_to": str(self.rel_to),
            "location": self.location.to_dict(),
            "package_type": self.package_type,
            "status": self.status,
            "metadata": json.dumps(self.metadata),
            "report": json.dumps(self.report),
            "namings": json.dumps(self.namings),
            "ov_path": str(self.ov_path),
            "kind": str(self.kind),
            "size": self.size,
            "uid": str(self.uid),
        }

    def from_dict(dic):
        if not Path(dic["path"]).exists():
            return False
        location = Location.from_dict(dic["location"])
        dcp = DCP(dic["path"], dic["rel_to"], location)
        try:
            dcp.uid = uuid.UUID(dic["uid"])
            dcp.package_type = dic["package_type"]
            dcp.status = dic["status"]
            dcp.metadata = json.loads(dic["metadata"])
            dcp.report = json.loads(dic["report"])
            dcp.namings = json.loads(dic["namings"])
            dcp.ov_path = dic["ov_path"]
            dcp.kind = dic["kind"]
            dcp.size = dic["size"]
            return dcp
        except Exception as e:
            print(e)
            return dcp