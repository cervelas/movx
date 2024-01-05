

from collections.abc import MutableMapping, MutableSequence


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


def _flat_gen(d, parent_key = None):
    for k, v in d.items():
        new_key = parent_key + (k,) if parent_key else (k,)
        if isinstance(v, MutableMapping):
            yield from flatten(v, new_key).items()
        elif isinstance(v, MutableSequence):
            v = { str(i): d for i, d in enumerate(v) }
            yield from flatten(v, new_key).items()
        else:
            yield new_key, v

def flatten(dic: MutableMapping, parent_key = None):
    return dict(_flat_gen(dic or {}, parent_key))

def finditem(dic, key, value):
    ret = []
    if dic.get(key) == value:
        ret.append(dic)
    else:
        for k, v in dic.items():
            if isinstance(v,dict):
                ret.extend(finditem(v, key, value))
            if isinstance(v,list):
                for e in v:
                    ret.extend(finditem(e, key, value))
    return ret