import pprint
import json
import uuid
from pathlib import Path

import clairmeta

class DCP:
    def __init__(self, folder, rel_to, location):
        self.path = Path(folder)
        self.rel_to = rel_to
        self.rel_path = self.path.relative_to(rel_to)
        self.location = location
        self.full_title = self.path.name
        self.uri = uuid.uuid5(uuid.NAMESPACE_X500, str(self.path.absolute)) #"%s-%s-%s" % (self.location, self.rel_path, self.full_title)
        self.title = self.full_title.split('_')[0]
        self.package_type = self.full_title.split('_')[-1]
        self.status = None
        self.dcp_metadata = {}
        self.ov_path = None
        self.parse()

    def asset(self, id):
        for a in self.assets:
            if a.id == str(id):
                return a
        return None
    
    def parse(self):
        try:
            self.dcp = clairmeta.DCP(self.path)
            self.dcp_metadata = self.dcp.parse()
            self.package_type = self.dcp_metadata.get("package_type", None)
        except Exception as e:
            print(e)

    def check(self, ov=None, cb=None):
        status, report = self.dcp.check( ov_path=ov,
        hash_callback=cb)
        
        for c in report.checks_failed():
            pprint.pprint(c.short_desc())
            pprint.pprint([ e.message for e in c.errors ])

        self.report = report

        return report

    def print(self):
        print(self.title)

    def to_dict(self):
        return {
            "title": str(self.title),
            "path": str(self.path),
            "rel_to": str(self.rel_to),
            "location": str(self.location),
            "package_type": self.package_type,
            "status": self.status,
            "metadata": json.dump(self.dcp_metadata),
            "ov_path": str(self.ov_path),
            "uri": str(self.uri),
        }

    def from_dict(dic):
        dcp = DCP(dic["path"], dic["rel_to"], dic["location"])
        dcp.uri = uuid.UUID(dic["uri"])
        dcp.package_type = dic["package_type"]
        dcp.status = dic["status"]
        dcp.metadata = json.parse(dic["metadata"])
        dcp.ov_path = dic["ov_path"]
        