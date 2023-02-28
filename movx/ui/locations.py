import random
import subprocess
import os
import webbrowser
import string
from ctypes import windll
from movx.core.movx import movx
from h2o_wave import app, Q, ui, main, on

@on('#location/{name}')
async def location_layout(q: Q, name):
    dcps = []
    for t, l in movx.dcps.items():
        for dcp in l:
            if dcp.location.name == name:
                dcps.append(dcp)
    
    q.page['dcp_list'] = ui.form_card(box='content',
        items=[
            ui.inline(justify="between", items = [ ui.text_xl("Location " + name), ui.button(name='refresh_dcps', label='refresh')] ),
            make_flat_dcps_table(dcps),
            ui.buttons([ui.button(name='edit_multiple', label='Edit Multiple...', primary=True)]),
        ]
    )

def show_locs_list(q):
    q.page['locations_sidebar'] = ui.form_card(box=ui.box('sidebar', size=0),
        items=[
            ui.inline(justify="between", items = [ ui.text_xl("Locations"), ui.button(name='show_add_location', label='add') ] ),
        ]
    )
    for n, l in movx.locations.items():
        q.page["dcp-" + n.replace(' ', '_')] = ui.form_card(box=ui.box(zone='sidebar', size='0'), 
                items= [
                    ui.text_l(str(n)),
                    ui.text_s(str(l.path.absolute())),
                ],
                commands = [ 
                        ui.command(name='hide_location', label='Hide', icon='hide', value=n),
                        ui.command(name='delete_location', label='Delete', icon='delete', value=n), 
                        ui.command(name='show_update_location', label='Update', icon='refresh', value=n) 
                    ]
                )

@on()
async def show_add_location(q):
    q.page['meta'].side_panel = ui.side_panel(title='Add a new location', items=[
        ui.textbox(name='location_name', label='Name'),
        ui.textbox(name='location_path', label='Path'),
        ui.button(name='update_location', label='New')
    ])
    await q.page.save()

@on()
async def show_update_location(q):
    location_name = q.args.show_update_location or ""
    location = movx.locations[location_name]
    q.page['meta'].side_panel = ui.side_panel(title='Update ' + location.name, items=[
        ui.textbox(name='location_name', label='Name', value=str(location.name)),
        ui.textbox(name='location_path', label='Path', value=str(location.path)),
        ui.button(name='update_location', label='Update')
    ])
    await q.page.save()

@on()
async def refresh_dcps(q):
    movx.scan()
    await q.page.save()

@on()
async def update_location(q):
    movx.update_locations(q.args.location_name, q.args.location_path)

@on()
async def delete_location(q):
    movx.del_location(q.args.delete_location)