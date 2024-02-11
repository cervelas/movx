import os
import json
from pathlib import Path
from h2o_wave import Q, ui, on, copy_expando

from movx.core import DEFAULT_CHECK_PROFILE, db, get_available_check_profiles, is_linux, is_win
from movx.gui import convert_size, get_windows_drives, get_linux_drives
from movx.core import check_profile_folder

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
                    loc.name,
                    loc.type.name,
                    loc.uri,
                    loc.path,
                    str(len(loc.dcps())),
                    convert_size(0, False),
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
                    ui.table_column(name="name", label="Name", min_width="100px"),
                    ui.table_column(name="type", label="Type", min_width="100px"),
                    ui.table_column(name="uri", label="URI", min_width="100px"),
                    ui.table_column(name="path", label="Path", min_width="500px"),
                    ui.table_column(name="dcps", label="DCP's"),
                    ui.table_column(name="size", label="Size"),
                ],
                rows=rows,
            ),
        ],
    )


@on()
async def show_add_location_panel(q):
    
    copy_expando(q.args, q.client)

    if q.client.show_add_location_panel or q.args.show_add_location_panel or q.client.location_type:
        
        q.client.show_add_location_panel = True

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


################
# TAGS
################

@on()
async def add_tag_dialog(q):
    q.page["meta"].dialog = ui.dialog(
        title="Add Tag",
        name="add_tag_dialog",
        items=[
            ui.textbox(
                name="new_tag_name",
                label="Name",
                value=q.args.new_tag_name or "",
                required=True,
            ),
            ui.color_picker(
                name="new_tag_color",
                label="Color",
                value=q.args.new_tag_color or "",
            ),
            ui.button(name="do_add_tag", label="Add"),
        ],
    )


def update_tag_dialog(q, tag):
    q.page["meta"].dialog = ui.dialog(
        title="Update Tag",
        name="update_tag_dialog",
        items=[
            ui.textbox(
                name="upd_tag_name", label="Name", value=tag.name, required=True
            ),
            ui.color_picker(name="upd_tag_color", label="Color", value=tag.color),
            ui.button(name="do_update_tag", label="Update", value=str(tag.id)),
        ],
    )

def delete_tag_dialog(q, tag):
    q.page["meta"].dialog = ui.dialog(
        title="Delete Tag",
        name="delete_tag_dialog",
        items=[
            ui.text_l("Do you really want to delete tag %s ?" % tag.name),
            ui.button(name="do_delete_tag", label="Update", value=str(tag.id)),
        ],
    )

def tags_card(q, tags):
    tags_commands = [
        ui.command(name="update_tag", label="Update", icon="Update"),
        ui.command(name="delete_tag", label="Delete", icon="delete"),
    ]

    rows = []

    for tag in tags:
        rows.append(
            ui.table_row(
                name=str(tag.id),
                cells=[
                    "",
                    tag.name,
                    tag.color,
                ],
            )
        )

    return ui.form_card(
        box=ui.box(zone="2cols"),
        items=[
            ui.inline(
                items=[
                    ui.text_xl("Tags"),
                    ui.button(name="add_tag_dialog", label="Add", icon="add"),
                    ui.button(
                        name="add_defaults_tags", label="Add Defaults", icon="add"
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
                ui.button(
                    name="dbutils_reset_db", label="Reset Database", icon="delete"
                ),
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
        if is_win():
            dirs = get_windows_drives()
        elif is_linux():
            dirs = get_linux_drives()
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

#################
# CHECK PROFILES
#################

@on()
async def new_profile_dialog(q: Q):

    profiles = get_available_check_profiles()

    q.page["meta"].dialog = ui.dialog(
        title="New Profile",
        name="new_profile_dialog",
        items=[
            ui.textbox(
                name="new_profile", label="Name", required=True,
            ),

            ui.dropdown(name="tpl_profile", label="Based on", required=True,
                    placeholder="Select the profile to base the new profile on",
                    choices=[ ui.Choice(name=str(f.resolve()), label=f.stem) for f in profiles ]),

            ui.button(name="create_profile", label="Create"),
        ],
    )
    await q.page.save()    

def check_profile_editor_card(q: Q):
    
    profiles = []
    editor_items = []

    for f in check_profile_folder.iterdir():
        if f.is_file():
            profiles.append(f)

    if q.args.edited_profile:

        profile = {}

        name = Path(q.args.edited_profile).name

        with open(q.args.edited_profile) as fp:
            profile = json.load(fp)

        levels = profile.get("criticality", [])
        warnings = [ name for name, level in levels.items() if level == "WARNING" ]
        errors = [ name for name, level in levels.items() if level == "ERROR" ]
        bypass = profile.get("bypass", [])
        allowed = profile.get("allowed_foreign_files", [])

        def h(arr):
            return "%spx" % max(17*len(arr)+8, 30)
        
        editor_items = [ 
            ui.text_xl("Edit %s Check Profile" % name), 
            ui.text_l("Warning Criticality Tests"),
            ui.textbox(name='warnings_tests', label='', width="400px",
                        value="\n".join(warnings), height=h(warnings),
                        multiline=True, spellcheck=False),
            
            ui.text_l("Error Criticality Tests"),
            ui.textbox(name='errors_tests', label='', 
                        value="\n".join(errors), height=h(errors),
                        multiline=True, spellcheck=False),
            
            ui.text_l("Bypassed Tests"),
            ui.textbox(name='bypass_tests', label='', placeholder="one test per line",
                        value="\n".join(bypass), height=h(bypass),
                        multiline=True, spellcheck=False),
            
            ui.text_l("Allowed Foreign Files"),
            ui.textbox(name='foreign_files', label='', placeholder="one file per line",
                        value="\n".join(allowed), height=h(allowed),
                        multiline=True, spellcheck=False),
            
            ui.textbox(name="profile_name", label="name", required=False, value=name, visible=False),
            ui.button(name="update_profile", label="Update") 
        ]

    return ui.form_card(
        box=ui.box(zone="2cols", size="0"),
        items=[
            ui.inline([
                ui.text_l("Profiles Editor"),
                ui.button(name="new_profile_dialog", label="New Profile", icon="Add")
            ]),
            
            ui.dropdown(name="edited_profile", label="Edit existing profile file", trigger=True,
                    placeholder="Select the file to edit", value=q.args.edited_profile,
                    choices=[ ui.Choice(name=str(f.resolve()), label=f.name) for f in profiles ]),


        ] + editor_items
    )
