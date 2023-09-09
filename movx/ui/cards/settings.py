import os
from pathlib import Path
from h2o_wave import ui, on

from movx.ui import convert_size, get_windows_drives

locations_commands = [
    ui.command(
        name="scan_location", label="Scan dcps", icon="SearchData", value="hide"
    ),
    ui.command(name="delete_location", label="Delete", icon="delete", value="show"),
    ui.command(
        name="show_update_location", label="Update", icon="refresh", value="update"
    ),
]


def locations_list_card(locations):
    rows = []

    for loc in locations:
        size = sum(file.stat().st_size for file in Path(loc.path).rglob("*"))
        rows.append(
            ui.table_row(
                name=str(loc.id),
                cells=[
                    "",
                    loc.name,
                    loc.path,
                    "0", #str(len(loc.dcps)),
                    convert_size(size, False),
                ],
            )
        )

    return ui.form_card(
        box=ui.box(zone="content", size="0"),
        items=[
            ui.inline(
                items=[
                    ui.text_xl("Locations"),
                    ui.button(
                        name="show_add_location", label="Add Location", icon="add"
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
                    ui.table_column(name="name", label="Name", min_width="500px"),
                    ui.table_column(name="path", label="Path", min_width="500px"),
                    ui.table_column(name="dcps", label="DCP's"),
                    ui.table_column(name="size", label="Size"),
                ],
                rows=rows,
            ),
        ],
    )


def add_location_panel(q):
    q.page["meta"].side_panel = ui.side_panel(
        title="Add a new location",
        items=[
            ui.textbox(name="location_name", label="Name", required=True),
            ui.textbox(name="location_path", label="Path", required=True),
            ui.button(name="add_location", label="Add & Scan"),
            ui.text(""),
        ] + dir_browser(q),
    )


def location_side_panel(q, loc):
    q.page["meta"].side_panel = ui.side_panel(
        title="Update " + loc.name,
        items=[
            ui.textbox(
                name="location_id", label="Id", value=str(loc.id), disabled=True
            ),
            ui.textbox(
                name="location_name", label="Name", value=str(loc.name), required=True
            ),
            ui.textbox(
                name="location_path", label="Path", value=str(loc.path), required=True
            ),
            ui.button(name="update_location", label="Update"),
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


def status_card(q, statuses):
    forms = []

    for status in statuses:
        forms.append(
            ui.inline(
                items=[
                    ui.textbox(name="status_update_name", value=status.name),
                    ui.color_picker(
                        name="status_color_picker",
                        label="",
                        value=status.color,
                        inline=True,
                    ),
                    ui.button(name="status_del", label="Delete", icon="delete"),
                ]
            )
        )

    return ui.form_card(
        box=ui.box(zone="content", size="0"),
        items=[
            ui.inline(
                items=[
                    ui.text_xl("Status"),
                    ui.button(name="status_add", label="Add", icon="add"),
                    ui.button(
                        name="status_add_defaults", label="Add Defaults", icon="add"
                    ),
                ]
            )
        ]
        + forms,
    )


db_utils = ui.form_card(
    box=ui.box(zone="content", size="0"),
    items=[
        ui.text_xl("Database Utilities"),
        ui.inline(
            items=[
                ui.button(
                    name="dbutils_del_all_locs", label="Delete Locations", icon="delete"
                ),
                ui.button(
                    name="dbutils_del_all_dcp", label="Delete DCP's", icon="delete"
                ),
                ui.button(
                    name="dbutils_del_all_tasks", label="Delete Tasks", icon="delete"
                ),
                ui.button(name="dbutils_del_all", label="Delete All", icon="delete"),
            ]
        ),
    ],
)

def dir_browser(q):
    dirs = []

    if not q.args.dir_cwd:
        # if application mode and windows
        q.args.cwd = ""
        dirs = get_windows_drives()
    else:
        if not q.args.cwd:
            q.args.cwd = Path(q.args.dir_cwd)
        else:
            q.args.cwd = Path(q.args.cwd) / (q.args.dir_cwd or "")
        dirs = [str(x) for x in q.args.cwd.iterdir() if x.is_dir()]
    
    return [
            ui.combobox(name='dir_cwd', trigger=True, label=str(q.args.cwd),
                choices=dirs),
    ]