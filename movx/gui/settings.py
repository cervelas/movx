import json
from pathlib import Path
import shutil
import traceback

from h2o_wave import Q, on, ui, copy_expando
from movx.core import locations, dcps, DEFAULT_CHECK_PROFILE
from movx.gui import notif, setup_page
from movx.core import db
from movx.gui.cards import debug_card
from movx.gui.cards.locations import location_del_dialog, locations_list_card, show_add_location_panel, update_location_panel
from movx.gui.cards.settings import (
    add_tag_dialog,
    check_profile_editor_card,
    update_tag_dialog,
    delete_tag_dialog,
    db_utils,
    tags_card,
)

@on("#settings")
async def settings(q: Q):
    setup_page(q, "Settings", layout="2cols")

    try:

        q.page["db_utils"] = db_utils

        q.page["status_utils"] = tags_card(q, db.Tags.get())

        q.page["check_profile_editor"] = check_profile_editor_card(q)
    except Exception as e:
        notif(q, str(e), "error")

    await q.page.save()


############
# LOCATIONS
############

############
# TAGS
############

@on()
def add_defaults_tags():
    """
    Add some default status
    """
    db.Tags("done", "#81ff83").add()
    db.Tags("check", "#81b1ff").add()
    db.Tags("todo", "#ffd447").add()
    db.Tags("blocked", "#ff8181").add()
    notif("Default Tags Added")

@on()
async def update_tag(q):
    tag = db.Tags.get(q.args.update_tag)
    update_tag_dialog(q, tag)
    await q.page.save()

@on()
async def delete_tag(q):
    tag = db.Tags.get(q.args.delete_tag)
    delete_tag_dialog(q, tag)
    await q.page.save()

@on()
async def do_add_tag(q):
    try:
        if q.args.new_tag_name and len(q.args.new_tag_name) == 0:
            q.args.new_tag_name = None
        tag = db.Tags(q.args.new_tag_name, q.args.new_tag_color)
        tag.add()
        q.page["meta"].dialog = None
        notif(q, "Tag %s Added" % tag)
    except Exception as e:
        notif(q, str("\n".join(e.args)), "error")

@on()
async def do_update_tag(q):
    try:
        tag = db.Tags.get(q.args.do_update_tag)
        tag.update(name=q.args.upd_tag_name, color=q.args.upd_tag_color)
        q.page["meta"].dialog = None
        await settings(q)
        notif(q, "Tag %s Updated" % tag.name)
    except Exception as e:
        notif(q, str("\n".join(e.args)), "error")

@on()
async def do_delete_tag(q):
    try:
        tag = db.Tags.get(q.args.do_delete_tag)
        tag.delete()
        q.page["meta"].dialog = None
        notif(q, "Tag %s Deleted" % tag.name)
        await settings(q)
    except Exception as e:
        notif(q, str("\n".join(e.args)), "error")


############
# PROFILE
############

@on()
async def create_profile(q):
    if q.args.tpl_profile and q.args.new_profile:
        new_profile = Path(q.args.tpl_profile).parent / q.args.new_profile
        shutil.copyfile(q.args.tpl_profile, "%s.json" % new_profile)
        notif(q, "%s profile created (%s.json)" % (q.args.new_profile, new_profile))
        #Path(q.args.tpl_profile).copy(q.args.new_profile)
        #Path.
    await settings(q)

@on()
async def update_profile(q):

    file = q.args.edited_profile

    crit = {}

    crit.update({
        n: "WARNING" for n in q.args.warnings_tests.split("\n")
    })

    crit.update({
        n: "ERROR" for n in q.args.errors_tests.split("\n")
    })

    if crit.get("default") is None:
        crit.update({ "default": "ERROR" })
        print("Added default entry ERROR level")

    profile = {
        "criticality": crit,
        "bypass": [],
        "foreign_files": [],
    }

    profile["bypass"] = q.args.bypass_tests.split("\n")

    profile["foreign_files"] = q.args.foreign_files.split("\n")

    with open(q.args.edited_profile, 'w') as fp: 
        json.dump(profile, fp)

    await settings(q)

############
# DBUTILS
############

@on()
async def dbutils_del_all_locs(q: Q):
    db.Location.clear()
    q.page["meta"].notification = "Deleted all Locations"
    # todo: notification
    await q.page.save()
    await settings(q)


@on()
async def dbutils_del_all_tasks(q):
    db.Job.clear()
    q.page["meta"].notification = "Deleted all Jobs"
    # todo: notification
    await q.page.save()
    await settings(q)


@on()
async def dbutils_del_all_dcps(q):
    db.DCP.clear()
    q.page["meta"].notification = "Deleted all DCPs"
    # todo: notification
    await q.page.save()
    await settings(q)


@on()
async def dbutils_del_all(q):
    db.Job.clear()
    db.DCP.clear()
    db.Location.clear()
    q.page["meta"].notification = "All things deleted !"

    # todo: notification
    await q.page.save()
    await settings(q)


@on()
async def dbutils_reset_db(q: Q):
    db.reset_db()
    q.page["meta"].notification = "Database reseted"
    # todo: notification
    await q.page.save()
    await settings(q)
