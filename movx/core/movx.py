import os
import json
import pprint
import uuid
from movx.core.dcp import DCP
from movx.core.location import Location
from pathlib import Path

class MovX:
    def __init__(self):
        self.local_db = Path.home() / ".movx" / "db.json"
        self.locations = {}
        self.dcps = {}
        self.load()

    def save(self):
        self.local_db.parent.mkdir(exist_ok=True, parents=True)
        db = { "movx_db": {
                    "locations": { n: l.to_dict() for n, l in self.locations.items() },
                    "dcps": { dcp.title: dcp.to_dict() for dcp in self.get_all() }
                }
            }
        db_str = json.dumps(db, indent=4)
        self.local_db.write_text(db_str)

    def load(self):
        if self.local_db.exists():
            with open(self.local_db) as f:
                db = json.load(f)
                db = db.get("movx_db", {})
                self.locations.update( 
                    { k: Location.from_dict(v) for k,v in db.get("locations", {}).items() } 
                )
                self.dcps.update( 
                    { k: DCP.from_dict(v) for k,v in db.get("dcps", {}).items() } 
                )

    def update_locations(self, name, path):
        self.locations.update( { name: Location(name, path) })
        self.save()

    def del_location(self, name):
        self.locations.pop(name, None)
        self.load()

    def scan(self):
        '''
        Scan for folders with ASSETMAP recursively
        '''
        self.dcps = {}

        for name, loc in self.locations.items():
            try:
                assetmaps = loc.scan_dcps()
                for am in assetmaps:
                    dcp = DCP(am.parent, loc.path, loc)

                    if dcp.title not in self.dcps:
                        self.dcps.update( { dcp.title: [] })
                    
                    self.dcps[dcp.title].append(dcp)

            except Exception as e:
                print(e)
        
        for dcp in self.get_all():
            if dcp.package_type != "OV":
                ovs = self.get_ov_dcps(dcp.title)
                if len(ovs) == 1:
                    dcp.ov = ovs[0]

    def check(self, title = None):
        '''
        Check all the dcp with the given title
        '''
        dcps = self.dcps.get(title)
        if dcps:
            for dcp in dcps:
                print("\t Check %s (%s)\n\n" % (dcp.uri))
                if dcp.check() is False:
                    return False
    
    def pretty_print(self):
        for title, dcps in self.dcps.items():
            print(title)
            for dcp in dcps:
                print("\t%s \n\t\t(%s)\n" % (dcp.full_title, dcp.uri))
    
    def get_all(self):
        dcps = []
        for t, d in self.dcps.items():
            dcps += d

        return dcps

    def get(self, uri):
        dcps = []
        for t, d in self.dcps.items():
            dcps += d

        dcp = None
        for d in dcps:
            if str(d.uri) == uri:
                dcp = d
        return dcp

    def get_ov_dcps(self, title):
        dcps = self.dcps.get(title)
        ovs = []
        if dcps:
            for dcp in dcps:
                if dcp.package_type == "OV":
                    ovs.append(dcp)
        return ovs

movx = MovX()