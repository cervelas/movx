import os
import json
from pathlib import Path
from h2o_wave import Q, ui, on

from movx.core import db, is_linux, is_win
from movx.gui import get_windows_drives, get_linux_drives
from movx.core.dcps import get_available_check_profiles

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
                name="new_profile",
                label="Name",
                required=True,
            ),
            ui.dropdown(
                name="tpl_profile",
                label="Based on",
                required=True,
                placeholder="Select the profile to base the new profile on",
                choices=[
                    ui.Choice(name=str(f.resolve()), label=f.stem) for f in profiles
                ],
            ),
            ui.button(name="create_profile", label="Create"),
        ],
    )
    await q.page.save()


def check_profile_editor_card(q: Q):
    editor_items = []

    profiles = get_available_check_profiles()

    if q.args.edited_profile:
        profile = {}

        name = Path(q.args.edited_profile).name

        with open(q.args.edited_profile) as fp:
            profile = json.load(fp)

        levels = profile.get("criticality", [])
        warnings = [name for name, level in levels.items() if level == "WARNING"]
        errors = [name for name, level in levels.items() if level == "ERROR"]
        bypass = profile.get("bypass", [])
        allowed = profile.get("allowed_foreign_files", [])

        def h(arr):
            return "%spx" % max(17 * len(arr) + 8, 30)

        editor_items = [
            ui.text_xl("Edit %s Check Profile" % name),
            ui.text_l("Warning Level Tests"),
            ui.textbox(
                name="warnings_tests",
                label="",
                width="400px",
                value="\n".join(warnings),
                height=h(warnings),
                multiline=True,
                spellcheck=False,
            ),
            ui.text_l("Error Level Tests"),
            ui.textbox(
                name="errors_tests",
                label="",
                value="\n".join(errors),
                height=h(errors),
                multiline=True,
                spellcheck=False,
            ),
            ui.text_l("Bypassed Tests"),
            ui.textbox(
                name="bypass_tests",
                label="",
                placeholder="one test per line",
                value="\n".join(bypass),
                height=h(bypass),
                multiline=True,
                spellcheck=False,
            ),
            ui.text_l("Allowed Foreign Files"),
            ui.textbox(
                name="foreign_files",
                label="",
                placeholder="one file per line",
                value="\n".join(allowed),
                height=h(allowed),
                multiline=True,
                spellcheck=False,
            ),
            ui.textbox(
                name="profile_name",
                label="name",
                required=False,
                value=name,
                visible=False,
            ),
            ui.button(name="update_profile", label="Update"),
        ]

    return ui.form_card(
        box=ui.box(zone="2cols", size="0"),
        items=[
            ui.inline(
                [
                    ui.text_l("Profiles Editor"),
                    ui.button(
                        name="new_profile_dialog", label="New Profile", icon="Add"
                    ),
                ]
            ),
            ui.dropdown(
                name="edited_profile",
                label="Edit existing profile file",
                trigger=True,
                placeholder="Select the file to edit",
                value=q.args.edited_profile,
                choices=[
                    ui.Choice(name=str(f.resolve()), label=f.stem) for f in profiles
                ],
            ),
        ]
        + editor_items,
    )
