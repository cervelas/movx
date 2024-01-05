import os
import json
from pathlib import Path
from h2o_wave import ui, on

from movx.core import DEFAULT_CHECK_PROFILE, db
from movx.gui import convert_size, get_windows_drives

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
                    str(len(loc.dcps())),
                    convert_size(size, False),
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
                    ui.table_column(name="name", label="Name", min_width="100px"),
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
        ]
        + dir_browser(q),
    )


def update_location_panel(q, loc):
    q.page["meta"].side_panel = ui.side_panel(
        title="Update " + loc.name,
        items=[
            ui.textbox(
                name="location_name", label="Name", value=str(loc.name), required=True
            ),
            ui.textbox(
                name="location_path", label="Path", value=str(loc.path), required=True
            ),
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


################
# STATUSES
################


@on()
async def add_status_dialog(q):
    q.page["meta"].dialog = ui.dialog(
        title="Add Status",
        name="add_status_dialog",
        items=[
            ui.textbox(
                name="new_status_name",
                label="Name",
                value=q.args.new_status_name or "",
                required=True,
            ),
            ui.color_picker(
                name="new_status_color",
                label="Color",
                value=q.args.new_status_color or "",
            ),
            ui.button(name="do_add_status", label="Add"),
        ],
    )


def update_tags_dialog(q, tag):
    q.page["meta"].dialog = ui.dialog(
        title="Update Tag",
        name="update_tag_dialog",
        items=[
            ui.textbox(
                name="update_tag_name", label="Name", value=tag.name, required=True
            ),
            ui.color_picker(name="upd_status_color", label="Color", value=tag.color),
            ui.button(name="do_update_tag", label="Update", value=str(tag.id)),
        ],
    )


def tags_card(q, tags):

    tags_commands = [
        ui.command(name="update_tags", label="Update", icon="Update"),
        ui.command(name="delete_tags", label="Delete", icon="delete"),
    ]

    rows = []

    for status in tags:
        rows.append(
            ui.table_row(
                name=str(status.id),
                cells=[
                    "",
                    status.name,
                    status.color,
                ],
            )
        )


    return ui.form_card(
        box=ui.box(zone="2cols"),
        items=[
            ui.inline(
                items=[
                    ui.text_xl("Tags"),
                    ui.button(name="add_status_dialog", label="Add", icon="add"),
                    ui.button(
                        name="status_add_defaults", label="Add Defaults", icon="add"
                    ),
                ]
            ),
            ui.table(
                name="statuses_table",
                columns=[
                    ui.table_column(
                        name="actions",
                        label="",
                        max_width="10px",
                        cell_type=ui.menu_table_cell_type(
                            name="commands", commands=tags_commands
                        ),
                    ),
                    ui.table_column(name="name", label="Name", min_width="200px"),
                    ui.table_column(
                        name="color",
                        label="Color",
                        filterable=True,
                        cell_type=ui.tag_table_cell_type(
                            name="tags",
                            tags=[
                                ui.tag(label=tags.color, color=tags.color)
                                for tags in db.Tags.get_all()
                            ]
                            + [ui.tag(label="N/A", color="$CCCCCC")],
                        ),
                    ),
                ],
                rows=rows,
            ),
        ],
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
                    name="dbutils_del_all_dcps", label="Delete DCP's", icon="delete"
                ),
                ui.button(
                    name="dbutils_del_all_tasks", label="Delete Tasks", icon="delete"
                ),
                ui.button(name="dbutils_del_all", label="Delete All", icon="delete"),
                ui.button(name="dbutils_reset_db", label="Reset Database", icon="delete"),
            ]
        ),
    ],
)


def dir_browser(q):
    items = []
    dirs = []
    parent = None
    if not q.args.dir_cwd:
        # if application mode and windows
        q.args.cwd = None
        dirs = get_windows_drives()
        items.append(
            ui.button(
                name="dir_cwd", value=None, link=True, icon="Folder", label="Root"
            )
        )
    else:
        if not q.args.cwd:
            q.args.cwd = Path(q.args.dir_cwd)
            parent = None
        else:
            q.args.cwd = Path(q.args.cwd) / (q.args.dir_cwd or "")
            parent = str(q.args.cwd.parent)
        items.append(
            ui.button(
                name="dir_cwd",
                value=parent,
                link=True,
                icon="Folder",
                label="🗁 " + str(q.args.cwd.parent),
            )
        )
        try:
            dirs = [str(x) for x in q.args.cwd.iterdir() if x.is_dir()]
        except Exception as e:
            dirs = []
            q.args.dir_cwd = None
            q.args.cwd = None

    for d in dirs:
        items.append(
            ui.button(
                name="dir_cwd", value=d, link=True, icon="Folder", label=" | 🗀 " + d
            )
        )

    return [ui.text_l(str(q.args.cwd or "/"))] + items + [ui.separator()]


def check_profile_card(q, profile):
    levels = profile.get("criticality", [])
    bypass = profile.get("bypass", [])
    allowed = profile.get("allowed_foreign_files", [])

    levels_items = []

    for name, level in levels.items():
        if name == "default":
            levels_items.append(
                ui.inline(
                    items=[
                        ui.textbox(
                            name="level_name", value=name, width="400px", readonly=True
                        ),
                        ui.dropdown(
                            name="level_picker",
                            label="",
                            choices=[
                                ui.choice(name="WARNING", label="WARNING"),
                                ui.choice(name="ERROR", label="ERROR"),
                            ],
                            value=level,
                            width="150px",
                        ),
                    ]
                )
            )
        else:
            levels_items.append(
                ui.inline(
                    items=[
                        ui.textbox(name="level_name", value=name, width="400px"),
                        ui.dropdown(
                            name="level_picker",
                            label="",
                            choices=[
                                ui.choice(name="WARNING", label="WARNING"),
                                ui.choice(name="ERROR", label="ERROR"),
                            ],
                            value=level,
                            width="150px",
                        ),
                        ui.button(
                            name="level_update", label="Update", icon="Save", value=name
                        ),
                        ui.button(
                            name="level_del", label="Delete", icon="delete", value=name
                        ),
                    ]
                )
            )

    bypass_items = []

    for name in bypass:
        bypass_items.append(
            ui.inline(
                items=[
                    ui.textbox(name="bypass_name", value=name, width="400px"),
                    ui.button(
                        name="bypass_update", label="Update", icon="Save", value=name
                    ),
                    ui.button(
                        name="bypass_del", label="Delete", icon="delete", value=name
                    ),
                ]
            )
        )

    allowed_items = []

    for name in allowed:
        allowed_items.append(
            ui.inline(
                items=[
                    ui.textbox(name="allowed_name", value=name, width="400px"),
                    ui.button(
                        name="allowed_update", label="Update", icon="Save", value=name
                    ),
                    ui.button(
                        name="allowed_del", label="Delete", icon="delete", value=name
                    ),
                ]
            )
        )

    return ui.form_card(
        box=ui.box(zone="2cols", size="0"),
        items=[ui.text_xl("Check Profile Editor"), ui.text_l("Tests Criticality")]
        + levels_items
        + [
            ui.button(name="add_level", label="Add Entry", icon="Add"),
            ui.separator(),
            ui.text_l("Test Bypass"),
        ]
        + bypass_items
        + [
            ui.button(name="add_bypass", label="Add Entry", icon="Add"),
            ui.separator(),
            ui.text_l("Ignored Foreign Files"),
        ]
        + allowed_items
        + [
            ui.button(name="add_allowed", label="Add Entry", icon="Add"),
        ],
    )
