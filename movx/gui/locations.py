import traceback
from pathlib import Path
import time

from h2o_wave import Q, ui, on, copy_expando

from movx.gui import notif, setup_page
from movx.core.db import Location, LocationType
from movx.core import dcps
from movx.core.locations import (
    agent_infos,
    get_root_path,
    scan_local,
    scan_agent,
    scan4dcps,
)
from movx.gui.cards.locations import (
    location_del_dialog,
    locations_list_card,
    show_add_location_panel,
    update_location_panel,
)

"""
ffmpeg -ss 00:04:01 -i .\Persona_FTR-1_F-177_XX-EN_20_2K_SEED_20220531_JIN_IOP_OV\Persona_FTR-1_F-177_XX-EN_20_2K_SEED_20220531_JIN_IOP_OV_b44dc5eb-52ad-44_j2c.mxf -frames:v 1 -y  output.png
"""


@on("#locs")
async def locations(q: Q):
    setup_page(q, "Locations List")

    q.page["locs_list"] = locations_list_card(Location.get_all())

    if q.client.adding_location is True:
        copy_expando(q.args, q.client)
        await show_add_location_panel(q)

    await q.page.save()


@on()
async def add_location(q: Q):
    copy_expando(q.args, q.client)

    try:
        loc = Location(
            q.client.location_name,
            q.client.location_path,
            uri=q.client.location_uri,
            type=LocationType(int(q.client.location_type)),
        )

        loc.add()
        notif(q, "Scan for dcps in %s ..." % loc.name)
        await q.page.save()
        _dcps = scan4dcps(loc)
        for dcp in _dcps:
            dcps.parse(dcp)
        q.client.adding_location = False

        notif(q, "%s dcps found in location %s" % (len(_dcps), loc.name))
        await locations(q)
    except Exception as e:
        print(e)
        print(traceback.format_exc())

        q.client.adding_location = True

        notif(q, "Error: %s" % str(e.args), "error")


@on()
async def show_update_location(q: Q):
    loc = Location.get(q.args.show_update_location)
    if loc:
        update_location_panel(q, loc)
    await q.page.save()


@on()
async def update_location(q):
    copy_expando(q.args, q.client)

    loc = Location.get(q.client.location_id)

    if loc:
        loc = loc[0]
        try:
            loc.update(
                name=q.client.location_name,
                path=q.client.location_path,
                uri=q.client.location_uri,
                type=LocationType(int(q.client.location_type)),
            )
            await locations(q)
            notif(q, "Location %s updated" % loc.name)

        except Exception as e:
            notif(q, str("\n".join(e.args)), "error")


@on()
async def prescan_location(q):
    copy_expando(q.args, q.client)

    q.client.show_add_location_panel = True

    type = LocationType(int(q.client.location_type))

    paths = []
    root_path = []
    name = ""

    if type == LocationType.Local:
        paths = scan_local(q.client.location_path)
        root_path = Path.cwd()
        name = "Directory"
    if type == LocationType.Agent:
        if len(q.client.location_uri) == 0:
            notif(q, "Empty URI !", "error")
            return
        paths = scan_agent(q.client.location_uri, q.client.location_path)
        root_path = agent_infos(q.client.location_uri)["root_path"]
        name = q.client.location_uri

    q.page["meta"].dialog = ui.dialog(
        title="Prescan Results for %s %s" % (type.name, name),
        name="prescan_dialog",
        closable=True,
        width="70%",
        items=[
            ui.text_l("Root path is %s" % root_path),
            ui.text("\n\n".join([str(Path(p).relative_to(root_path)) for p in paths])),
        ],
    )
    await q.page.save()


@on()
async def scan_location(q):
    loc = Location.get(q.args.scan_location)

    if loc:
        notif(q, "Scan location %s for dcp's..." % loc.name)
        await q.page.save()
        _dcps = scan4dcps(loc)
        notif(q, "Parsing locations")
        await q.page.save()
        for dcp in _dcps:
            dcps.parse(dcp)
            time.sleep(0.5)
        notif(q, "%s dcps found in location %s" % (len(_dcps), loc.name))
        await q.page.save()


@on()
async def delete_location(q):
    loc = Location.get(int(q.args.delete_location))

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
    loc = Location.get(int(q.args.ok_delete_loc))
    if loc:
        notif(q, "Location %s deleted" % loc.name)
        loc.delete()
    await locations(q)
