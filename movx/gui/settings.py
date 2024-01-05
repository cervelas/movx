import json
import time

from h2o_wave import Q, on, ui
from movx.core import locations, status, dcps, DEFAULT_CHECK_PROFILE
from movx.gui import setup_page
from movx.core import db
from movx.gui.cards import debug_card
from movx.gui.cards.settings import (
    locations_list_card,
    update_location_panel,
    location_del_dialog,
    add_location_panel,
    check_profile_card,
    update_tags_dialog,
    db_utils,
    tags_card,
)


@on("#settings")
async def settings(q: Q):
    setup_page(q, "Settings", layout="2cols")

    q.page["meta"].notification = ""

    profile = DEFAULT_CHECK_PROFILE

    with open(dcps.check_profile_file, "r") as fp:
        profile = json.load(fp)

    if q.args.status_add_defaults:
        status.add_defaults()

    q.page["locations_list"] = locations_list_card(db.Location.get())

    q.page["db_utils"] = db_utils

    q.page["status_utils"] = tags_card(q, db.Tags.get())

    q.page["check_profile_editor"] = check_profile_card(q, profile)

    if q.args.dir_cwd or q.args.show_add_location:
        add_location_panel(q)

    await debug_card(q)

    await q.page.save()


@on()
async def show_add_location(q):
    add_location_panel(q)
    await q.page.save()


@on()
async def add_location(q: Q, parse=True):
    if q.args.location_path:
        q.client.add_location_path = q.args.location_path
    if q.args.location_name:
        q.client.add_location_name = q.args.location_name
    try:
        loc = db.Location(q.client.add_location_path, q.client.add_location_name)
        loc.add()
        _dcps = locations.scan(loc)
        if parse:
            for dcp in _dcps:
                dcps.parse(dcp)
        await settings(q)
    except Exception as e:
        q.page["meta"].side_panel.items[1].textbox.error = "Error: %s" % str(e)
        await q.page.save()
        raise e


@on()
async def show_update_location(q: Q):
    loc = db.Location.get(q.args.show_update_location)
    if loc:
        update_location_panel(q, loc)
    await debug_card(q)
    await q.page.save()


@on()
async def update_location(q):
    loc = db.Location.get(q.args.location_id)

    if loc:
        try:
            loc.update(name=q.args.location_name, path=q.args.location_path)
            await settings(q)
        except Exception as e:
            q.page["meta"].side_panel.items[2].textbox.error = "Error: %s" % str(e)
            await q.page.save()
            raise e


@on()
async def scan_location(q):
    loc = db.Location.get(q.args.scan_location)

    if loc:
        locations.scan(loc)

    await settings(q)


@on()
async def delete_location(q):
    loc = db.Location.get(int(q.args.delete_location))

    if loc:
        location_del_dialog(q, loc)

    await q.page.save()


@on()
async def cancel_delete_loc(q):
    q.page["meta"].dialog = None
    await q.page.save()


@on()
async def ok_delete_loc(q):
    q.page["meta"].dialog = None
    loc = db.Location.get(int(q.args.ok_delete_loc))
    if loc:
        loc.delete()
    await settings(q)


@on()
async def update_status(q):
    status = db.Status.get(q.args.update_status)
    update_tags_dialog(q, status)
    await q.page.save()


@on()
async def do_add_status(q):
    try:
        status = db.Status(q.args.new_status_name, q.args.new_status_color)
        status.add()
        q.page["meta"].dialog = None
        q.page["meta"].notification = "Status %s Added" % status.name
        await q.page.save()
        await settings(q)

    except Exception as e:
        q.page["meta"].dialog.items[0].textbox.error = "Error: %s" % str(e)
        await q.page.save()


@on()
async def do_update_status(q):
    try:
        status = db.Status.get(q.args.do_update_status)
        status.update(name=q.args.upd_status_name, color=q.args.upd_status_color)
        q.page["meta"].dialog = None
        q.page["meta"].notification = "Status %s Updated" % status.name
        await q.page.save()
        await settings(q)
    except Exception as e:
        q.page["meta"].dialog.items[0].textbox.error = "Error: %s" % str(e)
        await q.page.save()
        raise e


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
