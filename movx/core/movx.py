import os
import json
import pprint
import uuid
import threading

from movx.core.dcp import DCP
from movx.core.location import Location, default_location
from pathlib import Path

lock = threading.Lock()

class MovX:
    '''
    Keep a list of locations and dcp's

    DCP management, scanning, checking

    Provide DBA layer by save() and load()
    '''
    def __init__(self):
        self.local_db = Path.home() / ".movx" / "db.json"
        self.locations = {}
        self.dcps = []
        self.load()

    def save(self):
        with lock:
            self.local_db.parent.mkdir(exist_ok=True, parents=True)
            # this is actually the database
            db = { "movx_db": {
                        "locations": { n: l.to_dict() for n, l in self.locations.items() },
                        "dcps": [ dcp.to_dict() for dcp in self.dcps ],
                    }
                }
            
            db_str = json.dumps(db, indent=4)
            self.local_db.write_text(db_str)

    def load(self, data=None):
        with lock:
            if data is None:
                if self.local_db.exists():
                    with open(self.local_db) as f:
                        data = json.load(f)
            if data:
                data = data.get("movx_db", {})
                self.locations.update( 
                    { k: Location.from_dict(v) for k, v in data.get("locations", {}).items() } 
                )
                self.dcps = [ DCP.from_dict(v) for v in data.get("dcps", []) ]
            else:
                self.locations.update( { default_location.name: default_location } )

    def update_locations(self, name, path):
        self.locations.update( { name: Location(name, path) })
        self.save()

    def del_location(self, name):
        self.locations.pop(name, None)
        self.save()

    def scan(self):
        '''
        Scan for folders with ASSETMAP recursively
        '''

        for name, loc in self.locations.items():
            try:
                assetmaps = loc.scan_dcps()
                for am in assetmaps:
                    dcp = DCP(am.parent, loc.path, loc)

                    dcp.parse()

                    if self.get_dcp(dcp.uid):
                        dcp.report = self.get_dcp(dcp.uid).report
                        self.dcps.remove(self.get_dcp(dcp.uid))
                    
                    self.dcps.append(dcp)

            except Exception as e:
                print(e)
        
        for dcp in self.dcps:
            if dcp.package_type != "OV":
                ovs = self.get_ov_dcps(dcp.title)
                if len(ovs) == 1:
                    dcp.ov = ovs[0]
        
        self.save()

    def check(self, title = None):
        '''
        Check all the dcp with the given title
        '''
        dcps = self.dcps.get(title)
        if dcps:
            for dcp in dcps:
                print("\t Check %s (%s)\n\n" % (dcp.uid))
                if dcp.check() is False:
                    return False
    
    def pretty_print(self):
        for title, dcps in self.dcps.items():
            print(title)
            for dcp in dcps:
                print("\t%s \n\t\t(%s)\n" % (dcp.full_title, dcp.uid))

    def get_dcp(self, uid):
        for dcp in self.dcps:
            if str(dcp.uid) == str(uid):
                return dcp
        return None

    def get_movie_dcps(self, title):
        return [ dcp for dcp in self.dcps if dcp.title == title ]
    
    def get_ov_dcps(self, title):
        dcps = self.get_movie_dcps(title)
        ovs = []
        if dcps:
            for dcp in dcps:
                if dcp.package_type == "OV":
                    ovs.append(dcp)
        return ovs

movx = MovX()