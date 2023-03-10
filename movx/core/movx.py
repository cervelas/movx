import os
import json
import pprint
import uuid
import threading

from movx.core.dcp import DCP, CHECK_PROFILE
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
        self.settings_file = Path.home() / ".movx" / "settings.json"
        self.dcps_db = Path.home() / ".movx" / "dcps.json"
        self.settings = {}
        self.locations = {}
        self.dcps = []
        self.load()

    def save_settings(self):
        with lock:
            self.settings_file.parent.mkdir(exist_ok=True, parents=True)

            settings = { 
                    "movx": {
                        "locations": { n: l.to_dict() for n, l in self.locations.items() },
                        "check_profile": CHECK_PROFILE,
                    }
                }
        
            settings_str = json.dumps(settings, indent=4)
            self.settings_file.write_text(settings_str)

    def save_dcps(self):
        with lock:
            self.dcps_db.parent.mkdir(exist_ok=True, parents=True)

            db = { "movx_dcps": {
                        "dcps": [ dcp.to_dict() for dcp in self.dcps ],
                    }
                }

            db_str = json.dumps(db, indent=4)
            self.dcps_db.write_text(db_str)

    def save(self):
        self.save_settings()
        self.save_dcps()

    def load_dcps(self, data=None):
        with lock:
            if data is None:
                if self.dcps_db.exists():
                    with open(self.dcps_db) as f:
                        data = json.load(f)
            if data:
                data = data.get("movx_dcps", {})
                self.dcps = []
                for v in data.get("dcps", []):
                    dcp = DCP.from_dict(v)
                    if dcp:
                        self.dcps.append(dcp)
                        dcp.location.dcps.append(dcp)

    def load_settings(self, data=None):
        with lock:
            if data is None:
                if self.settings_file.exists():
                    with open(self.settings_file) as f:
                        data = json.load(f)
            if data:
                data = data.get("movx", {})
                self.locations.update( 
                    { k: Location.from_dict(v) for k, v in data.get("locations", {}).items() } 
                )
            else:
                self.locations.update( { default_location.name: default_location } )

    def load(self):
        self.load_settings()
        self.load_dcps()

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
                    loc.dcps.append(dcp)

            except Exception as e:
                print(e)
        
        for dcp in self.dcps:
            if dcp.package_type != "OV":
                ovs = self.get_ov_dcps(dcp.title)
                if len(ovs) == 1:
                    dcp.ov_path = ovs[0].path

        self.dcps = [ dcp for dcp in self.dcps if dcp.path.exists() ]

        self.save()

    def check(self, title):
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
        for dcp in self.dcps:
            print("\t%s \n\t\t(%s)\n" % (dcp.full_title, dcp.uid))

    def get_dcp(self, uid):
        for dcp in self.dcps:
            if str(dcp.uid) == str(uid):
                return dcp
        return None

    def get_movie_dcps(self, title):
        return [ dcp for dcp in self.dcps if dcp.title == title ]
    
    def get_location_dcps(self, location):
        return [ dcp for dcp in self.dcps if dcp.location.path.absolute() == location.path.absolute() ]
    
    def get_ov_dcps(self, title):
        dcps = self.get_movie_dcps(title)
        ovs = []
        if dcps:
            for dcp in dcps:
                if dcp.package_type == "OV":
                    ovs.append(dcp)
        return ovs

movx = MovX()