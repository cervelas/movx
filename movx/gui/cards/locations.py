from movx.core import db
from movx.gui import convert_size


from h2o_wave import copy_expando, on, ui


def locations_list_card(locations):

    locations_commands = [
        ui.command(
            name="scan_location", label="Scan dcps", icon="SearchData", value="hide"
        ),
        ui.command(name="delete_location", label="Delete", icon="delete", value="show"),
        ui.command(
            name="show_update_location", label="Update", icon="refresh", value="update"
        ),
    ]

    rows = []

    for loc in locations:
        rows.append(
            ui.table_row(
                name=str(loc.id),
                cells=[
                    "",
                    "[%s](#loc/%s)" % (loc.name, loc.id),
                    loc.type.name,
                    loc.uri,
                    loc.path,
                    str(len(loc.dcps())),
                ],
            )
        )

    return ui.form_card(
        box=ui.box(zone="header", size="0"),
        items=[
            ui.inline(
                items=[
                    ui.text_xl("DCP Locations"),
                    ui.button(
                        name="show_add_location_panel", label="Add", icon="add"
                    ),
                ]
            ),
            ui.table(
                name="table",
                columns=[
                    ui.table_column(
                        name="actions",
                        label="",
                        max_width="25px",
                        cell_type=ui.menu_table_cell_type(
                            name="commands", commands=locations_commands
                        ),
                    ),
                    ui.table_column(name="name", label="Name", min_width="100px", cell_type=ui.markdown_table_cell_type(),),
                    ui.table_column(name="type", label="Type", min_width="100px"),
                    ui.table_column(name="uri", label="URI", min_width="100px"),
                    ui.table_column(name="path", label="Path", min_width="600px"),
                    ui.table_column(name="dcps", label="DCP's"),
                ],
                rows=rows,
            ),
        ],
    )


@on()
async def show_add_location_panel(q):

    q.client.adding_location = True

    items = [ui.dropdown(name="location_type", value=str(q.client.location_type), choices=[
                ui.Choice(name=str(db.LocationType.Local.value), label=db.LocationType.Local.name),
                ui.Choice(name=str(db.LocationType.Agent.value), label=db.LocationType.Agent.name),
            ], label="Type", required=True, trigger=True),
        ]

    if q.client.location_type == str(db.LocationType.Local.value):
        items += [
            ui.textbox(name="location_name", label="Name", value=q.client.location_name,required=True),
            ui.textbox(name="location_path", label="Path", value=q.client.location_path, required=True, placeholder = "Path on the host"),
            ui.button(name="prescan_location", label="Scan"),
            ui.button(name="add_location", label="Add"),
        ]

    elif q.client.location_type == str(db.LocationType.Agent.value):
        items += [
            ui.textbox(name="location_name", label="Name", value=q.client.location_name,required=True),
            ui.textbox(name="location_uri", label="Remote Agent ip addr with port", value=q.client.location_uri,
                        required=True, placeholder = "Remote agent address (e.g. 127.0.0.1:11011)"),
            ui.textbox(name="location_path", label="Path", value=q.client.location_path, required=True, placeholder = "Path on the remote"),
            ui.button(name="prescan_location", label="Scan"),
            ui.button(name="add_location", label="Add"),
        ]
    else:
        items += [ ui.text("Please select a proper Location Type") ]

    q.page["meta"].side_panel = ui.side_panel(
        title="Add a local folder",
        items=items,
    )
    await q.page.save()


def update_location_panel(q, loc):
    if loc.type == None:
        loc.type = db.LocationType.Local
    q.page["meta"].side_panel = ui.side_panel(
        title="Update " + loc.name,
        items=[
            ui.dropdown(name="location_type", value=str(loc.type.value), choices=[
                ui.Choice(name=str(db.LocationType.Local.value), label=db.LocationType.Local.name),
                ui.Choice(name=str(db.LocationType.Agent.value), label=db.LocationType.Agent.name),
            ], label="Type", required=True),
            ui.textbox(
                name="location_name", label="Name", value=str(loc.name), required=True
            ),
            ui.textbox(
                name="location_path", label="Path", value=str(loc.path), required=True
            ),
            ui.textbox(name="location_uri", label="Uri", value=str(loc.uri), required=False),
            ui.button(name="update_location", label="Update", value=str(loc.id)),
        ],
    )


def location_del_dialog(q, loc):
    q.page["meta"].dialog = ui.dialog(
        title="Delete ?",
        name="delete_loc",
        items=[
            ui.text(
                "Do you really want to delete the location *%s* and all the DCPs associated with it ?"
                % loc.name
            ),
            ui.buttons(
                [
                    ui.button(name="cancel_delete_loc", label="Cancel", primary=True),
                    ui.button(
                        name="ok_delete_loc",
                        label="Submit",
                        value=str(q.args.delete_location),
                    ),
                ]
            ),
        ],
    )