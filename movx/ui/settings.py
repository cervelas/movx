from datetime import timedelta

from h2o_wave import app, Q, main, on
from movx.core import locations, status
from movx.ui import setup_page
from movx.core import db
from movx.ui.cards.settings import locations_list_card, location_side_panel, location_del_dialog, db_utils, status_card


@on('#settings')
async def settings_layout(q: Q):
    
    setup_page(q, "Settings")

    q.page['locations_list'] = locations_list_card(locations.get_all())

    q.page['db_utils'] = db_utils

    q.page['status_utils'] = status_card(q, status.get_all())

    await q.page.save()

@on()
async def add_location(q):
    if q.args.location_path:
        q.client.add_location_path = q.args.location_path
    if q.args.location_name:
        q.client.add_location_name = q.args.location_name
    try:
        loc = locations.add(q.client.add_location_path , q.client.add_location_name)
        locations.scan(loc)
        await settings_layout(q)
    except Exception as e:
        print(e)
        q.page['meta'].side_panel.items[1].textbox.error = "Error: %s" % str(e)

@on()
async def show_update_location(q):
    loc = locations.get(q.args.show_update_location)
    if loc:
        location_side_panel(q, loc)
    await q.page.save()

@on()
async def update_location(q):
    loc = locations.get(q.args.location_id)
    
    if loc:
        try:
            update(loc, name=q.args.location_name, path=q.args.location_path)
            await settings_layout(q)
        except Exception as e:
            q.page['meta'].side_panel.items[2].textbox.error = "Error: %s" % str(e)

@on()
async def scan_location(q):
    loc = locations.get(q.args.scan_location)

    if loc:
        locations.scan(loc)

    await settings_layout(q)

@on()
async def delete_location(q):
    loc = locations.get(int(q.args.delete_location))

    if loc:
        location_del_dialog(q, loc)

    await q.page.save()

@on()
async def cancel_delete_loc(q):
    q.page['meta'].dialog = None
    await q.page.save()

@on()
async def ok_delete_loc(q):
    q.page['meta'].dialog = None
    loc = locations.get(int(q.args.ok_delete_loc))
    if loc:
        locations.delete(loc)
    await settings_layout(q)

@on()
async def status_add_defaults(q):
    status.add_defaults()
    await q.page.save()

@on()
async def dbutils_del_all_locs(q):
    db.clear(db.Location)
    #todo: notification
    await q.page.save()

@on()
async def dbutils_del_all_tasks(q):
    db.clear(db.Task)
    #todo: notification
    await q.page.save()

@on()
async def dbutils_del_all_dcps(q):
    db.clear(db.DCP)
    #todo: notification
    await q.page.save()

@on()
async def dbutils_del_all(q):
    db.clear(db.Task)
    db.clear(db.DCP)
    db.clear(db.Location)
    q.page['meta'].notification = 'And now for something completely different!'

    #todo: notification
    await q.page.save()