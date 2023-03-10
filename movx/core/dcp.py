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
            self.dcp._probeb = False
            self.metadata = self.dcp.parse(probe=True)
            self.package_type = self.metadata.get("package_type", "Unknown")
            self.size = self.metadata.get("size", "Unknown")

            if len(self.metadata.get("cpl_list", [])) > 0:
                self.namings = self.metadata["cpl_list"][0]["Info"]["CompositionPlaylist"]["NamingConvention"]
                self.kind = self.metadata["cpl_list"][0]["Info"]["CompositionPlaylist"]["ContentKind"]

        except Exception as e:
            print(e)

    def check(self, profile=None, cb=None):
        report = {}
        profile = profile or CHECK_PROFILE
        try:
            status, report = self.dcp.check(profile=CHECK_PROFILE, ov_path=self.ov_path,
            hash_callback=cb)
            
            for c in report.checks_failed():
                pprint.pprint(c.short_desc())
                pprint.pprint([ e.message for e in c.errors ])


            self.report = report.to_dict()
        except Exception as e:
            report['Message'] = "DCP Check failed:" + str(e)
            self.report = report
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

CHECK_PROFILE = {
    'criticality': {
        'default': 'ERROR',
        'check_dcnc_': 'WARNING',
        'check_*_xml': 'WARNING', # MOVX Custom
        'check_subtitle_cpl_language': 'WARNING', # MOVX Custom
        'check_dcp_foreign_files': 'WARNING',
        'check_assets_am_volindex_one': 'WARNING',
        'check_*_empty_text_fields': 'WARNING',
        'check_*_empty_text_fields_missing': 'ERROR',
        'check_*_xml_constraints_line_ending': 'WARNING',
        'check_cpl_contenttitle_annotationtext_match': 'WARNING',
        'check_cpl_contenttitle_pklannotationtext_match': 'WARNING',
        'check_assets_cpl_missing_from_vf': 'WARNING',
        'check_assets_cpl_labels_schema': 'WARNING',
        'check_assets_cpl_filename_uuid': 'WARNING',
        'check_certif_multi_role': 'WARNING',
        'check_certif_date_overflow': 'WARNING',
        'check_picture_cpl_avg_bitrate': 'WARNING',
        'check_picture_cpl_resolution': 'WARNING',
        'check_subtitle_cpl_reel_number': 'WARNING',
        'check_subtitle_cpl_empty': 'WARNING',
        'check_subtitle_cpl_uuid_case': 'WARNING',
        'check_subtitle_cpl_duplicated_uuid': 'WARNING',
        'check_subtitle_cpl_first_tt_event': 'WARNING',
        'check_picture_cpl_archival_framerate': 'WARNING',
        'check_picture_cpl_hfr_framerate': 'WARNING',
        'check_sound_cpl_format': 'WARNING',
        'check_sound_cpl_channel_assignments': 'WARNING',
        'check_atmos_cpl_channels': 'WARNING',
        'check_atmos_cpl_objects': 'WARNING',
    },
    # Checker options
    # Bypass is a list of check names (function names)
    'bypass': [
        #'check_assets_pkl_hash'
    ],
}
