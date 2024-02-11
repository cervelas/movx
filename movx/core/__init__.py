from collections.abc import MutableMapping, MutableSequence
import sys
import json
from pathlib import Path
import importlib.metadata

version = importlib.metadata.version('movx')

DEFAULT_CHECK_PROFILE = {
    "criticality": {
        "default": "ERROR",
        "check_dcnc_": "WARNING",
        "check_dcp_foreign_files": "WARNING",
        "check_assets_am_volindex_one": "WARNING",
        "check_*_empty_text_fields": "WARNING",
        "check_*_empty_text_fields_missing": "ERROR",
        "check_*_xml_constraints_line_ending": "WARNING",
        "check_cpl_contenttitle_pklannotationtext_match": "WARNING",
        "check_cpl_contenttitle_annotationtext_match": "WARNING",
        "check_assets_cpl_missing_from_vf": "WARNING",
        "check_assets_cpl_labels_schema": "WARNING",
        "check_assets_cpl_filename_uuid": "WARNING",
        "check_certif_multi_role": "WARNING",
        "check_certif_date_overflow": "WARNING",
        "check_picture_cpl_avg_bitrate": "WARNING",
        "check_picture_cpl_resolution": "WARNING",
        "check_subtitle_cpl_reel_number": "WARNING",
        "check_subtitle_cpl_empty": "WARNING",
        "check_subtitle_cpl_uuid_case": "WARNING",
        "check_subtitle_cpl_duplicated_uuid": "WARNING",
        "check_subtitle_cpl_first_tt_event": "WARNING",
        "check_picture_cpl_archival_framerate": "WARNING",
        "check_picture_cpl_hfr_framerate": "WARNING",
        "check_sound_cpl_format": "WARNING",
        "check_sound_cpl_channel_assignments": "WARNING",
        "check_atmos_cpl_channels": "WARNING",
        "check_atmos_cpl_objects": "WARNING",
        # Custom MOVX settings
        "check_*_xml": "WARNING",
        "check_subtitle_cpl_language": "WARNING",
    },
    # Checker options
    # Bypass is a list of check names (function names)
    "bypass": ["check_assets_pkl_hash"],
}

check_profile_folder = Path.home() / ".movx" / "check_profiles"

default_check_profile = check_profile_folder / "default.json"

def init_check_profile():
    if not check_profile_folder.exists():
        check_profile_folder.mkdir()

    if not default_check_profile.exists():
        with open(default_check_profile, "w") as fp:
            json.dump(DEFAULT_CHECK_PROFILE, fp)

def get_available_check_profiles():
    profiles = []

    for f in check_profile_folder.iterdir():
        if f.is_file():
            profiles.append(f)

    return profiles

def _flat_gen(d, parent_key=None):
    for k, v in d.items():
        new_key = parent_key + (k,) if parent_key else (k,)
        if isinstance(v, MutableMapping):
            yield from flatten(v, new_key).items()
        elif isinstance(v, MutableSequence):
            v = {str(i): d for i, d in enumerate(v)}
            yield from flatten(v, new_key).items()
        else:
            yield new_key, v


def flatten(dic: MutableMapping, parent_key=None):
    return dict(_flat_gen(dic or {}, parent_key))


def finditem(dic, key, value):
    ret = []
    if dic.get(key) == value:
        ret.append(dic)
    else:
        for k, v in dic.items():
            if isinstance(v, dict):
                ret.extend(finditem(v, key, value))
            if isinstance(v, list):
                for e in v:
                    ret.extend(finditem(e, key, value))
    return ret

def is_linux():
    return sys.platform.startswith("linux")

def is_win():
    return sys.platform.startswith("win")


def check_report_to_dict(checkreport):

    report = checkreport.to_dict()

    report["succeeded"] = [s.to_dict() for s in checkreport.checks_succeeded()]
    report["fails"] = [f.to_dict() for f in checkreport.checks_failed()]
    report["errors"] = [
        v.to_dict()
        for v in checkreport.checks_failed()
        if v.errors[0].criticality == "ERROR"
    ]
    report["warnings"] = [
        v.to_dict()
        for v in checkreport.checks_failed()
        if v.errors[0].criticality == "WARNING"
    ]
    report["bypassed"] = [b.to_dict() for b in checkreport.checks_bypassed()]

    return report

